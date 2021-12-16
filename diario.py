from operator import itemgetter
import fitz
import json
import re
from unidecode import unidecode

def fonts(doc, granularity=False):
	styles = {}
	font_counts = {}
	for page in doc:
		blocks = page.get_text("dict")["blocks"]
		for b in blocks:
			if b['type'] == 0:
				for l in b["lines"]:
					for s in l["spans"]:
						if granularity:
							identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
							styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'], 'color': s['color']}
						else:
							identifier = "{0}".format(s['size'])
							styles[identifier] = {'size': s['size'], 'font': s['font']}
						font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage
	font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)
	if len(font_counts) < 1:
		raise ValueError("Zero discriminating fonts found!")
	return font_counts, styles

def font_tags(font_counts, styles):
	p_style = styles[font_counts[0][0]] 
	p_size = p_style['size']
	font_sizes = []
	for (font_size, count) in font_counts:
		font_sizes.append(float(font_size))
	font_sizes.sort(reverse=True)
	idx = 0
	size_tag = {}
	for size in font_sizes:
		idx += 1
		if size == p_size:
			idx = 0
			size_tag[size] = '<p>'
		if size > p_size:
			size_tag[size] = '<h{0}>'.format(idx)
		elif size < p_size:
			size_tag[size] = '<s{0}>'.format(idx)
	return size_tag

def headers_para(doc, size_tag):
	header_para = [] 
	first = True 
	previous_s = {}  
	for page in doc:
		blocks = page.get_text("dict")["blocks"]
		for b in blocks:  
			if b['type'] == 0: 
				block_string = "" 
				for l in b["lines"]: 
					for s in l["spans"]: 
						if s['text'].strip(): 
							if first:
								previous_s = s
								first = False
								block_string = size_tag[s['size']] + s['text']
							else:
								if s['size'] == previous_s['size']:

									if block_string and all((c == "|") for c in block_string):
										block_string = size_tag[s['size']] + s['text']
									if block_string == "":
										block_string = size_tag[s['size']] + s['text']
									else:  
										block_string += " " + s['text']
								else:
									header_para.append(block_string)
									block_string = size_tag[s['size']] + s['text']
								previous_s = s
					block_string += "|"
				header_para.append(block_string)
	return header_para

def removeHeaders(elements):
	#Define header
	for i, e in enumerate(elements):
		if "Pará , " in e and "ANO " in e and "| Nº " in e:
			header = e
			break
	#Cleanup header		
	for i, e in enumerate(elements):
		if e == header:
			elements.pop(i-1)
			elements.pop(i-1)
			elements.pop(i-1)
			elements.pop(i-1)
	return elements

def indexIn ( elements, item ):
	for i, x in enumerate(elements):
		if item in x:
			return elements.index(x);

def clear ( str ):
	return re.sub('<[^<]+?>', '', str).strip()

def tipo ( str ):
	tipos = ["ADITIVO", "ATA", "DECRETO", "PORTARIA", "TERMO"]
	for t in tipos:
		if t in str.upper():
			return t
	return ""

def formatPost( elements ):
	e = {}
	if len(elements)>2:
		#Rastreabilidade
		#e["elements_original"] = elements
		#Removo cabeçalho eventual
		if unidecode(elements[1]) == unidecode(elements[3]):
			del(elements[0])
			del(elements[0])
			del(elements[0])
		if unidecode(elements[0]) == unidecode(elements[2]):
			del(elements[0])
			del(elements[0])
		if elements[1] == "":
			if unidecode(elements[0]) != unidecode(elements[2]):
				elements[0]+=elements[2]
				del(elements[1])
				del(elements[1])
		if elements[2] == "":
			del(elements[2])
		e["origem"] = clear(elements[0])
		e["tipo"] = tipo(clear(elements[1]))
		e["assunto"] = clear(elements[1])
		if "<p>Publicado por:" in elements:
			lastConteudo = elements.index("<p>Publicado por:")-1
		elif indexIn(elements, "<p>Código Identificador: "):
			lastConteudo = indexIn(elements, "<p>Código Identificador: ")-1
		else:
			lastConteudo = len(elements)
		if(lastConteudo>2):
			e["conteudo"] = clear(' '.join(elements[2:lastConteudo]))
		else:
			e["conteudo"] = clear(elements[2])
		if(e["tipo"] == ""):
			e["tipo"] = tipo(clear(e["conteudo"]))
		if "<p>Publicado por:" in elements:
			e["publicado_por"] = clear(elements[elements.index("<p>Publicado por:")+1])
		if indexIn(elements, "<p>Código Identificador: "):
			e["codigo_identificador"] = clear(elements[indexIn(elements, "<p>Código Identificador: ")].replace("<p>Código Identificador: ",""))
	return e

def lookPosts ( elements ):
	xPointer = 0
	ret = []
	for i, e in enumerate(elements):
		#if i>1 and e=="":
		if i>1 and "Código Identificador:" in e:
			#print("xPointer+1:")
			#print(xPointer+1)
			#print("i+1:")
			#print(i+1)
			#if(xPointer+1==16):
			ret.append(formatPost(elements[xPointer+1:i+1]))
			xPointer = i+1
	return ret

def removes ( elements, xfrom, xto ):
	ifrom = indexIn(elements, xfrom)
	ito = indexIn(elements, xto)
	ret = []
	for i, x in enumerate(elements):
		if not(i>=ifrom and i<=ito):
			ret.append(x)
	return ret

def removesDoubleLines ( elements ):
	ret = []
	for i, x in enumerate(elements):
		if len(x)>1:
			x = x.replace("|","")
		else:
			x = "||"
		ret.append(x.replace("||",""))
	return ret

def sanitize ( elements ):
	for i, e in enumerate(elements):
		if e == "<p>SANEPAR ":
			elements[i-1]+= elements[i]
			del(elements[i])
		if e == "<p>DE 2021. " or e=="<p>ESTADO DO PARÁ ":
			elements[i-1]+= clear(e)
			del(elements[i])
	return elements

def main():

	out = {}
	doc = fitz.open('diario.pdf')

	#Parametrizo os estilos do documento
	font_counts, styles = fonts(doc, granularity=False)
	size_tag = font_tags(font_counts, styles)
	elements = headers_para(doc, size_tag)

	#Inicializo o cabeçalho do retorno
	out["nome"] = elements[1].split("•")[1].strip()
	out["ano"] = elements[1].split("•")[2].split("|")[0].replace("ANO","").strip()
	out["numero"] = elements[1].split("•")[2].split("|")[1].replace("Nº","").strip()
	out["data"] = elements[1].split("•")[0].replace("<p>Pará ,","").strip()

	#Removo cabeçalho/rodapé
	elements = removeHeaders(elements)

	#Removo quebras de linha duplicadas
	elements = removesDoubleLines(elements)

	#Removo primeira publicação, ref ao expediente
	elements = removes(elements, "", "modernização e transparência da gestão municipal.")
	elements = removes(elements, "", "")

	#Removo inconsistências mapeadas 
	elements = sanitize(elements)

	#Busco e formato as publicações encontradas
	elements = lookPosts(elements)

	#Elenco os resultados
	out["resultado"] = elements

	#Persisto os dados encontrados no json
	with open("output.json", 'w') as json_out:
		json.dump(out, json_out)


if __name__ == '__main__':
	main()