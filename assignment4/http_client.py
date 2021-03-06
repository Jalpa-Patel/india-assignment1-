import socket
from urllib.parse import urlparse
import sys
__author__ = "jasvinder"


# creates an INET, STREAMING socket
# input:
#   url:String - takes the valid url to make tcp connection
#   port: Integer - take the port number to connect
# output:
#   TCPSocket - returns a tcp socket object for further communication.
def tcp_connection(url, port):
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  clientSocket.connect((url, port))
  return clientSocket

# Parses the URL into six components.i.e scheme, network location, path, parameters, query and fragment
# input:
#   url_name:String - takes the valid url passed
# output:
#   String - parsed Url into 6 components
def parse_url(url_name):
  return urlparse(url_name)

# User request for sending user input URL as HTTP request ending with two empty lines
# input:
#   url_name:String - takes the valid url passed
#   method_type:String - takes Http method type,i.e generally, POST or GET
# output:
#   get_request:String - returns the valid Http Request according to method type
def encode_http_request(path, method_type):
  protocol_type = 'HTTP/1.0'
  get_request = ''.join([method_type,' ', path,' ',protocol_type, '\r','\n','\r','\n'])
  return get_request

# Sends the passed http_request request over passed tcp socket object.
# input:
#   tcp_connection:TCP Socket object - takes the object of the TCP connection established
#   http_request:String - takes the valid Http Request according to method type i.e GET or POST method
# output:
#   Bytes: returns the Http request made in bytes to send it further for communication
def send_http_request(tcp_connection, http_request):
  return tcp_connection.send(str.encode(http_request))

# Reads the Http header of the response from tcp_connection socket.
# input:
#   tcp_connection:TCP Socket object - takes the object of the TCP connection established
#output:
#   http_headers: String - gives the HTTP header of the response
def read_http_header(tcp_connection):
  http_headers = ['HTTP/1.1 200 OK']# initialising headers too 22 as it has already been read to determine whether its 200 or not.
  while(True):
    response = tcp_connection.recv(1).decode('utf-8')
    if(response == '\r'):
      http_headers.append(response)
      response = tcp_connection.recv(3).decode('utf-8')
      if(response == '\n\r\n'):
        http_headers.append(response)
        break
      else:
        http_headers.append(response)

    else:
      http_headers.append(response)
  return ''.join(http_headers)

# Checks whether the response is 200 or not from the tcp socket.
# input:
#   tcp_connection:TCP Socket object - takes the object of the TCP connection established
#output:
#    Boolean : True for 200 False for all other http status code.
def http_status_200(tcp_connection):
  http_status = tcp_connection.recv(15).decode('utf-8')
  print(http_status)
  if(http_status.startswith('HTTP/1.1 200 OK')):
    return True
  return False

# Reads the body of the Http response as binary
# input:
#   tcp_connection:TCP Socket object - takes the object of the TCP connection established
#output:
#   list - gives the body of the Http response, as binary data
def read_http_body_as_binary(tcp_connection):
  http_body = []
  response = tcp_connection.recv(1024)
  while(response):
    http_body.append(response)
    response = tcp_connection.recv(1024)
  return http_body

# Decodes http header
# input:
#   http_header: Http header string.
#output:
#    list - list of http header strings.
def decode_http_header(http_header):
  return http_header.strip().split('\r\n')

# Reads the decoded http header
# input:
#   decoded_http_header: list of decoded http header
#output:
#    'String: tells whether type is text in binary
def find_content_type(decoded_http_header):
  #print(decoded_http_header)
  for value in decoded_http_header:
    if(value.startswith('Content-Type:')):
      if(value.startswith('Content-Type: text/html')):
        return 'text'
      else:
        return 'binary'

# Reads the string and the file name and saves the string on the file.
# input:
#   string_data_to_be_written:String - String of text to be written on the file
#   file_name: String- file name.
#output:
#    None
def save_text_data(string_data_to_be_written, file_name):
  with open(file_name, 'w+') as file:
    file.write(string_data_to_be_written)

# Reads the string and the file name and saves the string on the file.
# input:
#   binary_data_array_to_be_written:List - List of Byte to be written on the file
#   file_name: String- file name.
#output:
#    None
def save_binary_data(binary_data_array_to_be_written, file_name):
    #binary_data_to_be_written = str.encode(string_data_to_be_written)
    with open(file_name, 'bw') as file:
      for value in binary_data_array_to_be_written:
        file.write(value)



# Reads the string and the file name and saves the string on the file.
# input:
#   url_name:String - Url of the resource to be downloaded.
#   saveheader: Boolean- default is True. This is a flag for stating whether the header or not.
#output:
#    None
def call_http_server(url_name, saveheader = True):
  parsed_url = parse_url(url_name)
  tcp_socket = tcp_connection(parsed_url.netloc, 80)
  http_request = encode_http_request(parsed_url.path, 'GET')
  send_http_request(tcp_socket, http_request)
  print(url_name)
  if(http_status_200(tcp_socket)):
    http_header = read_http_header(tcp_socket)
    http_data = read_http_body_as_binary(tcp_socket)
    decoded_message = decode_http_header(http_header)
    file_name = parsed_url.path.split('/')[-1]
    if saveheader:
      header_file_name = file_name +  '.header'
      save_text_data(http_header, header_file_name)
    if(find_content_type(decoded_message) == 'text'):
      text_file_name = file_name + '.html'
      save_binary_data(http_data, text_file_name)
    elif(find_content_type(decoded_message) == 'binary'):
      save_binary_data(http_data, file_name)
  else:
      print("http status not 200")
  tcp_socket.close()

if __name__ == "__main__":
  call_http_server(sys.argv[1])
