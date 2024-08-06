from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

# from rasa_core.domain import Domain
# from rasa_core.trackers import EventVerbosity

import logging
logger = logging.getLogger(__name__)

import requests
import json

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.events import AllSlotsReset
from rasa_sdk.events import Restarted
from rasa_sdk.executor import CollectingDispatcher


class ActionExtractFlightInfo(Action):
    def name(self):
        return 'action_extract_flight_info'
        
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        source = tracker.get_slot('source')
        destination = tracker.get_slot('destination')
        date = tracker.get_slot('date')

        if not source:
            source = next(tracker.get_latest_entity_values("source"), None)
            if source:
                return [SlotSet('source', source)]
            else:
                dispatcher.utter_message("Where are you flying from?")
                return []

        if not destination:
            destination = next(tracker.get_latest_entity_values("destination"), None)
            if destination:
                return [SlotSet('destination', destination)]
            else:
                dispatcher.utter_message("Where are you flying to?")
                return []

        if not date:
            date = next(tracker.get_latest_entity_values("date"), None)
            if date:
                return [SlotSet('date', date)]
            else:
                dispatcher.utter_message("When do you want to fly?")
                return []

        dispatcher.utter_message(f"I have your flight from {source} to {destination} on {date}. Is that correct?")
        return []

		 
class SaveOrigin(Action):
	def name(self):
		return 'action_save_origin'
		
	def run(self, dispatcher, tracker, domain):
		orig = next(tracker.get_latest_entity_values("source"), None)
		print(orig)
		if not orig:
			dispatcher.utter_message("Please enter a valid airport code")
			return [UserUtteranceReverted()]
		return [SlotSet('source',orig)]
	


class SaveDestination(Action):
	def name(self):
		return 'action_save_destination'
		
	def run(self, dispatcher, tracker, domain):
		dest = next(tracker.get_latest_entity_values("destination"), None)
		if not dest:
			dispatcher.utter_message("Please enter a valid airport code")
			return [UserUtteranceReverted()]
		return [SlotSet('destination',dest)]
		
		
class SaveDate(Action):
	def name(self):
		return 'action_save_date'
		
	def run(self, dispatcher, tracker, domain):
		inp = next(tracker.get_latest_entity_values("date"), None)
		if not inp:
			dispatcher.utter_message("Please enter a valid date")
			return [UserUtteranceReverted()]
		return [SlotSet('date',inp)]
		
class ActionSlotReset(Action): 	
    def name(self): 		
        return 'action_slot_reset' 	
    def run(self, dispatcher, tracker, domain): 		
        return[AllSlotsReset()]
		

		
from bs4 import BeautifulSoup
import urllib.request
import re


class GetFlightStatus(Action):
    def name(self):
        return 'action_get_flight'
        
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        source = tracker.get_slot('source')
        destination = tracker.get_slot('destination')
        date = tracker.get_slot('date')
        
        if not source or not destination or not date:
            dispatcher.utter_message("Some slot values are missing.")
            return []
        
        flight_data = {
    "BOM": {  # Mumbai
        "DEL": {  # Delhi
            "20-01-2025": "Airline A: Rs. 5000, Airline B: Rs. 5200",
            "25-01-2025": "Airline C: Rs. 5100, Airline D: Rs. 5300",
        },
        "CCU": {  # Kolkata
            "20-01-2025": "Airline E: Rs. 5500, Airline F: Rs. 5600",
            "25-01-2025": "Airline G: Rs. 5700, Airline H: Rs. 5800",
        },
        "BLR": {  # Bengaluru
            "20-01-2025": "Airline M: Rs. 5900, Airline N: Rs. 6000",
            "25-01-2025": "Airline O: Rs. 6100, Airline P: Rs. 6200",
        },
        "HYD": {  # Hyderabad
            "20-01-2025": "Airline Q: Rs. 6300, Airline R: Rs. 6400",
            "25-01-2025": "Airline S: Rs. 6500, Airline T: Rs. 6600",
        },
        "MAA": {  # Chennai
            "20-01-2025": "Airline U: Rs. 6700, Airline V: Rs. 6800",
            "25-01-2025": "Airline W: Rs. 6900, Airline X: Rs. 7000",
        }
    },
    "DEL": {  # Delhi
        "BOM": {  # Mumbai
            "20-01-2025": "Airline I: Rs. 4900, Airline J: Rs. 5000",
            "25-01-2025": "Airline K: Rs. 5100, Airline L: Rs. 5200",
        },
        "CCU": {  # Kolkata
            "20-01-2025": "Airline Y: Rs. 5300, Airline Z: Rs. 5400",
            "25-01-2025": "Airline AA: Rs. 5500, Airline BB: Rs. 5600",
        },
        "BLR": {  # Bengaluru
            "20-01-2025": "Airline CC: Rs. 5700, Airline DD: Rs. 5800",
            "25-01-2025": "Airline EE: Rs. 5900, Airline FF: Rs. 6000",
        },
        "HYD": {  # Hyderabad
            "20-01-2025": "Airline GG: Rs. 6100, Airline HH: Rs. 6200",
            "25-01-2025": "Airline II: Rs. 6300, Airline JJ: Rs. 6400",
        },
        "MAA": {  # Chennai
            "20-01-2025": "Airline KK: Rs. 6500, Airline LL: Rs. 6600",
            "25-01-2025": "Airline MM: Rs. 6700, Airline NN: Rs. 6800",
        }
    },
    "CCU": {  # Kolkata
        "BOM": {  # Mumbai
            "20-01-2025": "Airline OO: Rs. 6900, Airline PP: Rs. 7000",
            "25-01-2025": "Airline QQ: Rs. 7100, Airline RR: Rs. 7200",
        },
        "DEL": {  # Delhi
            "20-01-2025": "Airline SS: Rs. 7300, Airline TT: Rs. 7400",
            "25-01-2025": "Airline UU: Rs. 7500, Airline VV: Rs. 7600",
        },
        "BLR": {  # Bengaluru
            "20-01-2025": "Airline WW: Rs. 7700, Airline XX: Rs. 7800",
            "25-01-2025": "Airline YY: Rs. 7900, Airline ZZ: Rs. 8000",
        },
        "HYD": {  # Hyderabad
            "20-01-2025": "Airline AAA: Rs. 8100, Airline BBB: Rs. 8200",
            "25-01-2025": "Airline CCC: Rs. 8300, Airline DDD: Rs. 8400",
        },
        "MAA": {  # Chennai
            "20-01-2025": "Airline EEE: Rs. 8500, Airline FFF: Rs. 8600",
            "25-01-2025": "Airline GGG: Rs. 8700, Airline HHH: Rs. 8800",
        }
    },
    "BLR": {  # Bengaluru
        "BOM": {  # Mumbai
            "20-01-2025": "Airline III: Rs. 8900, Airline JJJ: Rs. 9000",
            "25-01-2025": "Airline KKK: Rs. 9100, Airline LLL: Rs. 9200",
        },
        "DEL": {  # Delhi
            "20-01-2025": "Airline MMM: Rs. 9300, Airline NNN: Rs. 9400",
            "25-01-2025": "Airline OOO: Rs. 9500, Airline PPP: Rs. 9600",
        },
        "CCU": {  # Kolkata
            "20-01-2025": "Airline QQQ: Rs. 9700, Airline RRR: Rs. 9800",
            "25-01-2025": "Airline SSS: Rs. 9900, Airline TTT: Rs. 10000",
        },
        "HYD": {  # Hyderabad
            "20-01-2025": "Airline UUU: Rs. 10100, Airline VVV: Rs. 10200",
            "25-01-2025": "Airline WWW: Rs. 10300, Airline XXX: Rs. 10400",
        },
        "MAA": {  # Chennai
            "20-01-2025": "Airline YYY: Rs. 10500, Airline ZZZ: Rs. 10600",
            "25-01-2025": "Airline AAAA: Rs. 10700, Airline BBBB: Rs. 10800",
        }
    },
    "HYD": {  # Hyderabad
        "BOM": {  # Mumbai
            "20-01-2025": "Airline CCCC: Rs. 10900, Airline DDDD: Rs. 11000",
            "25-01-2025": "Airline EEEE: Rs. 11100, Airline FFFF: Rs. 11200",
        },
        "DEL": {  # Delhi
            "20-01-2025": "Airline GGGG: Rs. 11300, Airline HHHH: Rs. 11400",
            "25-01-2025": "Airline IIII: Rs. 11500, Airline JJJJ: Rs. 11600",
        },
        "CCU": {  # Kolkata
            "20-01-2025": "Airline KKKK: Rs. 11700, Airline LLLL: Rs. 11800",
            "25-01-2025": "Airline MMMM: Rs. 11900, Airline NNNN: Rs. 12000",
        },
        "BLR": {  # Bengaluru
            "20-01-2025": "Airline OOOO: Rs. 12100, Airline PPPP: Rs. 12200",
            "25-01-2025": "Airline QQQQ: Rs. 12300, Airline RRRR: Rs. 12400",
        },
        "MAA": {  # Chennai
            "20-01-2025": "Airline SSSS: Rs. 12500, Airline TTTT: Rs. 12600",
            "25-01-2025": "Airline UUUU: Rs. 12700, Airline VVVV: Rs. 12800",
        }
    },
    "MAA": {  # Chennai
        "BOM": {  # Mumbai
            "20-01-2025": "Airline WWWW: Rs. 12900, Airline XXXX: Rs. 13000",
            "25-01-2025": "Airline YYYY: Rs. 13100, Airline ZZZZ: Rs. 13200",
        },
        "DEL": {  # Delhi
            "20-01-2025": "Airline AAAAA: Rs. 13300, Airline BBBBB: Rs. 13400",
            "25-01-2025": "Airline CCCCC: Rs. 13500, Airline DDDDD: Rs. 13600",
        },
        "CCU": {  # Kolkata
            "20-01-2025": "Airline EEEEE: Rs. 13700, Airline FFFFF: Rs. 13800",
            "25-01-2025": "Airline GGGGG: Rs. 13900, Airline HHHHH: Rs. 14000",
        },
        "BLR": {  # Bengaluru
            "20-01-2025": "Airline IIIII: Rs. 14100, Airline JJJJJ: Rs. 14200",
            "25-01-2025": "Airline KKKKK: Rs. 14300, Airline LLLLL: Rs. 14400",
        },
        "HYD": {  # Hyderabad
            "20-01-2025": "Airline MMMMM: Rs. 14500, Airline NNNNN: Rs. 14600",
            "25-01-2025": "Airline OOOOO: Rs. 14700, Airline PPPPP: Rs. 14800",
        }
    }
}

        if source in flight_data and destination in flight_data[source] and date in flight_data[source][destination]:
            flight_info = flight_data[source][destination][date]
            dispatcher.utter_message(f"Here is the list of carriers with their fare for {source} to {destination} on {date}:")
            dispatcher.utter_message(flight_info)
        else:
            dispatcher.utter_message("Sorry, I could not find flight information for your query.")
        
        return []
	# def run(self, dispatcher, tracker, domain):
	# 	orig=tracker.get_slot('from')
	# 	dest=tracker.get_slot('to')
	# 	dat=tracker.get_slot('date')
	# 	quote_page = "https://flights.makemytrip.com/makemytrip/search/O/O/E/1/0/0/S/V0/{}_{}_{}?contains=false&remove="
	# 	page=urllib.request.urlopen(quote_page.format(orig,dest,dat))
	# 	soup = BeautifulSoup(page, 'html.parser')
	# 	list1=[]
	# 	message=soup.find_all('label',attrs={'class':'flL mtop5 mleft3 vallabel'})
	# 	dispatcher.utter_message("Here is the list of carriers with their fare")
	# 	for a in message:
	# 		list1.append(a.text)	
	# 	message1=soup.find_all('span',attrs={'class':'flR'})
	# 	list2=[]
	# 	for b in message1:
	# 		if "Rs." in b.text:
	# 			list2.append(re.sub('\s+', '', b.text))
	# 	for i in range(len(list1)):
	# 		dispatcher.utter_message(list1[i]+" : "+list2[i])
	# 	return []