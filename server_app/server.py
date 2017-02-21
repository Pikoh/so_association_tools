import sys

from meta import *
from models import *
from auth import *
from views import *
from oauth import *
from filters import *

if __name__ == "__main__":
    if len(sys.argv) > 1:
        from database import init_db, upload_csv, upload_csv_from_file, update_most_viewed
        if str(sys.argv[1]) == "--init_db":
            init_db()
            quit()
        elif str(sys.argv[1]) == "--upload_csv":
            debug_print = str(sys.argv[2]) == "--debug" if len(sys.argv) > 2 else False
            upload_csv("./csv_data_" + LANGUAGE + "/", debug_print)
            quit()
        elif "--upload_csv_from_file" in str(sys.argv[1]):
            debug_print = str(sys.argv[2]) == "--debug" if len(sys.argv) > 2 else False
            upload_csv_from_file("./csv_data_" + LANGUAGE + "/" + str(sys.argv[1]).split("=")[1], debug_print)
            quit()    
        elif str(sys.argv[1]) == "--update_most_viewed":
            update_most_viewed()
            quit()

    app.run()
