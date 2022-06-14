

def range_dates_between():
	import datetime

	start = datetime.datetime.strptime("30-05-2022", "%d-%m-%Y")
	end = datetime.datetime.strptime("05-06-2022", "%d-%m-%Y")
	date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end  -start ).days +1 )]
	mydates=[]
	for date in date_generated:
		mydates.append((date.strftime("%d-%m-%Y")))
	return(mydates)

print(range_dates_between())



# import schedule
# import time

# def job(t):
#     print ("I'm working...")
#     return

# schedule.every().day.at("01:00").do(job,'It is 01:00')

# while True:
#     schedule.run_pending()
#     time.sleep(60) # wait one minute