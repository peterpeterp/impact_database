


class bibliography(object):
	def __init__(self,test=None):
		self._articles=[]
		self._meta={'author':{},'year':{},'title':{},'publisher':{},'keywords':{}}

	def clean(self,string):
		string=string.replace('{','').replace('}','').replace(',','')
		while string[0]==' ':string=''.join(string[1:])
		while string[-1]==' ':string=''.join(string[0:-1])
		return string

	def extract_keywords(self,string):
		string=string.replace('{','').replace('}','')
		while string[0]==' ':string=''.join(string[1:])
		while string[-1]==' ':string=''.join(string[0:-1])
		keywords=string.split(',')
		keywords=list(filter(None, keywords))
		keywords=[key.lower().replace('\\&','and') for key in keywords]
		return keywords

	class article(object):

		def __init__(SELF,bibtex,bibli,index):
			SELF.description=bibtex
			SELF.author='Na'
			SELF.title='Na'
			SELF.year='Na'
			SELF.publisher='Na'
			SELF.url='Na'
			SELF.keywords=[]
			for line in bibtex.split('\n'):
				if len(line.split('='))>1:
					if bibli.clean(line.split('=')[0])=='url': 
						url=bibli.clean(line.split('=')[1])
						SELF.url=url
					if bibli.clean(line.split('=')[0])=='author': 
						author=bibli.clean(line.split('=')[1])
						SELF.author=author
						if author not in bibli._meta['author']:bibli._meta['author'][author]=[]
						bibli._meta['author'][author].append(index)
					if bibli.clean(line.split('=')[0])=='title': 
						title=bibli.clean(line.split('=')[1])
						SELF.title=title
						if title not in bibli._meta['title']:bibli._meta['title'][title]=[]
						bibli._meta['title'][title].append(index)
					if bibli.clean(line.split('=')[0])=='year': 
						year=bibli.clean(line.split('=')[1])
						SELF.year=year
						if year not in bibli._meta['year']:bibli._meta['year'][year]=[]
						bibli._meta['year'][year].append(index)
					if bibli.clean(line.split('=')[0])=='publisher': 
						publisher=bibli.clean(line.split('=')[1])
						SELF.publisher=publisher
						if publisher not in bibli._meta['publisher']:bibli._meta['publisher'][publisher]=[]
						bibli._meta['publisher'][publisher].append(index)
					if bibli.clean(line.split('=')[0])=='keywords': 
						keywords=bibli.extract_keywords(line.split('=')[1])
						SELF.keywords=keywords


			for key in SELF.keywords:
				if key not in bibli._meta['keywords']:bibli._meta['keywords'][key]=[]
				bibli._meta['keywords'][key].append(index)					



	def add_article(self,bibtex):
		new=self.article(bibtex=bibtex,bibli=self,index=len(self._articles))
		self._articles.append(new)

	def filter(self,filters):
		to_filter={}
		selected=range(len(self._articles))

		for key in filters.keys():
			for accepted in filters[key]:
				for item in selected:
					if item not in self._meta[key][accepted]:
						selected.remove(item)
				
		return(selected)


	def check_occurence_of_keyword(self,selected):

		tmp=[]
		for i in selected:
			#print self._articles[i].keywords
			tmp+=self._articles[i].keywords

		freq_dict={}
		for key in tmp:
			if key not in freq_dict.keys():
				freq_dict[key]=0
			freq_dict[key]+=1

		word_count=list()
		for key in freq_dict.keys():
			word_count.append((key,freq_dict[key]))
			#word_count.append((key,float(freq_dict[key])/len(tmp)))

		return word_count,tmp









