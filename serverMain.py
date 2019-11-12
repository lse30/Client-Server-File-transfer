"""
COSC264 ASSIGNMENT 1: Socket Assignment
July 17th
Liam Seymour
95314668
Code for Server side
"""

#declare Imports
import socket
import sys
from datetime import datetime

#Declare Magic Number here so it can be easily changes
MAGICNUM = 0x497E


def quitProgram():
    """Simple program so it is clear when the Server is shut"""
    print("Program exited")
    sys.exit()

def getPortNum():
    """Prompts the client for a specific port number
    or recieves from the terminal"""
    try:
        #For running through terminal.
        portNum = int(sys.argv[1])
    except ValueError:
        # if user doesnt enter a number
        print("ValueError: Input " + str(portNum) + " is not a number")
        quitProgram()
    if portNum < 1024 or portNum > 64000: # check port number is valid
        print("Invalid Port number: must be between 1024 and 64000.")
        quitProgram()
    elif len(sys.argv) != 1:
        print("Server requires a single argument of a Port Number between 1024 and 64000")
        quitProgram()
    else:
        return portNum

def createBoundSocket(portNum):
    """Attempts to create a new socket and
    binds it to the choosen port number"""
    print("Building Socket and binding it to Port Number " + str(portNum) + "...")
    try: #error handling incase building a socket fails
        server = socket.socket()
    except:
        print("An error has occurred while creating a socket, Server will now close")
        quitProgram()
    try:
        server.bind(('', portNum))
    except OSError: #port is currently in use
        print("OSError: An error has occurred while binding port number, Server will now close")
        server.close()
        quitProgram()
    print("Success")
    return server

def listenIn(socket):
    """Creates a listening channel"""
    try:
        socket.listen(5)
    except:
        socket.close()
        print("An error has occurred while listening, Server will now close")
        quitProgram()
    print("Socket is now listening")

def checkRequest(fileRequestArray):
    """Checks that the given request is valid
    returns the filename to retrive and also a flag (status code)"""
    if len(fileRequestArray) < 5: #must be at lease 5 bytes for the header
        print("Recieved Request Array is incorrect.")
        return None, 0

    #required parameters for request array
    Type = 1

    #recieved values from array
    recievedMagicNo = (fileRequestArray[0] << 8) + fileRequestArray[1]
    recievedType = fileRequestArray[2]
    recievedFileLength = (fileRequestArray[3] << 8) + fileRequestArray[4]
    #check that it fits all the style rules for a request array
    if MAGICNUM != recievedMagicNo or recievedType != Type or len(fileRequestArray) != 5 + recievedFileLength\
            or recievedFileLength < 1 or recievedFileLength > 1024:
        print("Recieved Request Array is incorrect.")
        return None, 0
    else:
        #retrieves fileName from packet
        fileName = (fileRequestArray[5:(5 + recievedFileLength)])
        fileName = fileName.decode('utf-8')
        return fileName, 1

def buildFile(file, statusCode):
    """creates a return packet """
    MagicNo_left = MAGICNUM >> 8
    MagicNo_right = (MAGICNUM & 0xFF)
    type = 2

    if statusCode == 0:
        #Creates a packet with status code 0 and datalength 0 (failure packet).
        output = bytearray([MagicNo_left, MagicNo_right, type, statusCode, 0, 0, 0, 0])
    else:
        #creates a packet to return with the contents of the file requested
        contents = file.read()
        dataLength = len(contents)
        dataLength_1 = dataLength >> 24
        dataLength_2 = (dataLength & 0xFF0000) >> 16
        dataLength_3 = (dataLength & 0xFF00) >> 8
        dataLength_4 = (dataLength & 0xFF)
        output = bytearray([MagicNo_left, MagicNo_right, type, statusCode,
                            dataLength_1, dataLength_2, dataLength_3, dataLength_4]) + contents
    return output

def openFile(filename):
    """Opens the file for reading from or returns an error and a flag if file does
    not exist"""
    try:
        file = open(filename, "rb")
    except NameError:
        print("That file does not exist")
        return None, 0
    return file, 1


def main():
    """The main program for the server"""
    portNum = getPortNum() #get port number and checks that its valid
    boundSock = createBoundSocket(portNum) #binds the socket
    listenIn(boundSock)


    while True: #begins an infinite loop while the socket is listening
        clientSock, addr = boundSock.accept() #accepts incomming connection.
        currentTime = datetime.now().strftime('%H:%M:%S') #gets the time
        print("Server connected at " + currentTime + " at IP = " + addr[0] + " and PortNo = " + str(addr[1]))
        fileRequestArray, address = clientSock.recvfrom(4096)
        fileName, statusCode = checkRequest(fileRequestArray) #see if the request is valid
        if statusCode == 1:
            file, statusCode = openFile(fileName)
        if statusCode == 0: #returns an error statement to the client
            print("Recieved Request File for unknown file \'" + fileName + "\'.")
            fileResponse = buildFile(file, statusCode)
            clientSock.send(fileResponse)
            print("Server successfully sent error response to client in " + str(bytesSent) + " bytes.")
            clientSock.close()
        else: #return the file from the server to the client
            print("Recieved Request File for \'" + fileName + "\'.")

            fileResponse = buildFile(file, statusCode)
            clientSock.send(fileResponse)
            bytesSent = len(fileResponse)
            print("Server successfully sent " + str(bytesSent) + " bytes.")
            file.close()
            clientSock.close()




if __name__ == "__main__":
    main()