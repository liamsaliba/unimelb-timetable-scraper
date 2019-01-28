import scrapy	
import datetime

TT_COL_NAMES = ['Class Code', 'Description', 'Day', 'Start', 'Finish', 'Duration', 'Weeks', 'Location', 'Class Dates', 'Start Date']

class SubjectsSpider(scrapy.Spider):
	name = 'subjects'

	# COMP20007 COMP30027 CHIN10005 MAST20004
	# MAST20009 PHYC20012 JAPN10001 COMP20005
	subjects = input("Enter subject codes, space separated: ").split(" ")
	start_urls = ['https://handbook.unimelb.edu.au/2019/subjects/' + subj for subj in subjects]	

	def parse_timetable(self, response):
		data = response.meta['data']
		timetable = {}
		# gives COMP20007/U/1/SM1
		period_names = [x.strip("\n\t ").split("\xa0")[0][9:] for x in response.css("div h3 ::text").extract()]
		tables = response.css("table.cyon_table")
		for i, table in enumerate(tables):
			print("{} . Found {} - {}".format(datetime.datetime.now().isoformat(' '), period_names[i], data["Subject"]))
			parts = period_names[i].split("/")
			# Wondering if it's possible to not have those values ...
			if parts[1] != "U":
				print("Not U  !!")
			if parts[2] != "1":
				print("Not 1  !!")

			sem = parts[3]
			
			events = []
			for row in table.css("tbody tr"):
				# values within row
				values = row.css("td ::text").extract()
				# convert to dictionary
				event = dict([TT_COL_NAMES[i], values[i]] for i in range(len(TT_COL_NAMES)))
				event["Subject Name"] = data["Subject"]
				events.append(event)
			timetable[sem] = events

		data['Timetable'] = timetable

		print("{} - Parsed {} ({})".format(datetime.datetime.now().isoformat(' '), data["Subject"], data['Code']))

		yield data

	def parse(self, response):
		data = {}
		data["Subject"] = response.css("span.header--course-and-subject__main ::text").extract_first().split(" (")[0]

		infobox = response.css('div.course__overview-box tr')

		# Parse infobox
		for line in infobox:
			field = line.css('th ::text').extract_first()
			value = line.css('td').xpath("string(.)").extract_first()
			if field == 'Subject code':
				data["Code"] = value
		
		print("{} + Parsing {} ({})".format(datetime.datetime.now().isoformat(' '), data["Subject"], data['Code']))

		yield scrapy.Request(
			response.urljoin("https://sws.unimelb.edu.au/2019/Reports/List.aspx?objects=" + data['Code'] + "&weeks=1-52&days=1-7&periods=1-56&template=module_by_group_list"),
			callback=self.parse_timetable,
			meta={'data': data}
		)