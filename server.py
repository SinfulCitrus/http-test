from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import json
from urllib import parse

HOST = "localhost"
PORT = 8000

dbpath = "./"
nosql_filename = "nosql.json"

class BirthdayServer(HTTPServer):
    

    def __init__(self, *args, **kwargs):

        global nosql

        nosql = {}

        if os.path.exists(dbpath+nosql_filename):
            with open(dbpath+nosql_filename, "r") as f:
                nosql = json.load(f)
                print("NoSQL Birthday DB loaded.")
        else:
            with open(dbpath+nosql_filename, "w") as f:
                json.dump(nosql, f)
                print("NoSQL Birthday DB created.")

        nosql["kacper"] = "19/08"
        
        super(self.__class__, self).__init__(*args, **kwargs)

class BirthdayHTTP(BaseHTTPRequestHandler):

    def do_GET(self):
        
        print("===== GET REQUEST =====")

        print(self.headers)

        try:
            # Get the GET request query - aka the name
            query = parse.urlparse(self.path).query
            queries = [x for x in query.split("&")]
            queries_dict = {}
            for query in queries:
                query_split = query[:query.find("=")], query[query.find("=")+1:]
                queries_dict[query_split[0]] = query_split[1]

            # list entries
            if "list" in queries_dict.keys():
                
                limit = len(nosql) if not queries_dict["list"].isdigit() else int(queries_dict["list"])

                listEntries = []
                for i, name in enumerate(nosql.keys()):
                    listEntries.append(f"{name}")
                    if i+1 >= limit:
                        break
                resp = "\n".join(listEntries)

                # Form header
                self.send_response(200)
                self.send_header("Content-type", "text")
                self.end_headers()

                # Send response
                self.wfile.write(resp.encode("utf-8"))

                pass
            else:

                # Get the birthday of the user
                birthday = nosql[queries_dict["name"]]

                # Form header
                self.send_response(200)
                self.send_header("Content-type", "text")
                self.end_headers()

                # Send response
                self.wfile.write(birthday.encode("utf-8"))

        except TypeError as ex:
            self.send_error(400, "Empty GET Request")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
        except KeyError as ex:
            self.send_error(404, "User doesn't exist")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
        except Exception as ex:
            self.send_error(400, "Malformed GET Request")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

        print("=======================")

    def do_POST(self):
        
        print("===== POST REQUEST =====")

        # Get the GET request query - aka the name
        query = parse.urlparse(self.path).query
        queries = [x for x in query.split("&")]
        queries_dict = {}
        for query in queries:
            query_split = query[:query.find("=")], query[query.find("=")+1:]
            queries_dict[query_split[0]] = query_split[1]

        print(self.request)

        try:
            content_len = int(self.headers.get('Content-Length'))
            body = self.rfile.read(content_len).decode()

            exists = queries_dict["name"] in nosql.keys()
            nosql[queries_dict["name"]] = body

            with open(dbpath+nosql_filename, "w") as f:
                json.dump(nosql, f)
                print("NoSQL Birthday DB updated.")

            # Form header
            self.send_response(200)
            self.send_header("Content-type", "text")
            self.end_headers()

            # Send response
            if exists:
                self.wfile.write(f"{queries_dict['name']}'s birthday was updated.".encode("utf-8"))
            else:
                self.wfile.write(f"{queries_dict['name']}'s birthday was saved.".encode("utf-8"))

        except TypeError as ex:
            self.send_error(400, "Empty POST Request")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
        except Exception as ex:
            self.send_error(400, "Malformed POST Request")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

        print("========================")

    def do_DELETE(self):
        
        print("===== DELETE REQUEST =====")

        print(self.headers)

        try:
            # Get the DELETE request query - aka the name
            query = parse.urlparse(self.path).query
            queries = [x for x in query.split("&")]
            queries_dict = {}
            for query in queries:
                query_split = query[:query.find("=")], query[query.find("=")+1:]
                queries_dict[query_split[0]] = query_split[1]

            # Delete the user entry
            del nosql[queries_dict["name"]]

            with open(dbpath+nosql_filename, "w") as f:
                json.dump(nosql, f)
                print("NoSQL Birthday DB updated.")

            # Form header
            self.send_response(200)
            self.send_header("Content-type", "text")
            self.end_headers()

            # Send response
            self.wfile.write("User removed from the db.".encode("utf-8"))

        except TypeError as ex:
            self.send_error(400, "Empty DELETE Request")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
        except KeyError as ex:
            self.send_error(404, "User doesn't exist")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
        except Exception as ex:
            self.send_error(400, "Malformed DELETE Request")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

        print("=======================")


server = BirthdayServer((HOST, PORT), BirthdayHTTP)
print("Birthday Server started 🎂🥳🎉\n")
server.serve_forever()
server.server_close()