"""
COSC264 ASSIGNMENT 1: Socket Assignment
July 17th
Liam Seymour
95314668
Code for Client side
"""

#declare Imports
import socket
import sys
import time

#declare global variables
MAGICNUM = 0x497E
MAXBYTES = 4096

def quitProgram():
    """Simple program so it is clear when the client is shut"""
    print("Program exited")
    sys.exit()

def getData():
    """gets the data on IP, portnum and the file request from terminal"""
    if len(sys.argv) != 3:
        print("3 Parameters required (IP, portNum, fileName")
        quitProgram()
    try: #Attempts to get data straight from terminal args
        IP = sys.argv[1]
        portNum = sys.argv[2]
        filename = sys.argv[3]
    except:
        print("Error retriving Parameters")
        quitProgram()

    return checkData(IP, portNum, filename) #sends the retrieved parameters to check they are valid

def checkData(IP, portNum, filename):
    """confirms that all the data given is valid and file is not already saved locally
        IP is converted into dotted.decimal.form at this stage too in preperation of next step"""
    print("Checking given Parameters...")
    try:
        hostAddress = socket.gethostbyaddr(IP)
        IP = hostAddress[-1][0]
    except socket.gaierror:
        print("IP Error: Name or service not known")
        quitProgram()
    except socket.herror:
        print("IP Error: Host name lookup failure")
        quitProgram()

    try:
        portNum = int(portNum)
    except ValueError:
        print("ValueError: Input not a number") #if user doesnt enter a number
        quitProgram()
    if portNum < 1024 or portNum > 64000: # check port number is valid
        print("Invalid Port number: must be between 1024 and 64000.")
        quitProgram()

    try:
        fileOpen = open(filename)
        print("File already exists on local host.")
        print("System will now exit.")
        quitProgram()
    except:
        pass # file does not exist

    print("Success")
    return IP, portNum, filename

def createByteFile (filename):
    """creates the packet consisting of:
        -A MagicNo == 0x497E
        -Type == 1
        -filename length
        -filename"""
    print("Preparing file request record for \'" + str(filename) + "\'...")

    MagicNo_left = MAGICNUM >> 8
    MagicNo_right = (MAGICNUM & 0xFF)
    type = 1

    byteFileName = filename.encode('utf-8')
    filenameLength = len(byteFileName)
    if filenameLength > 1024:
        print("File name is too long, system will now close")
        quitProgram()
    filenameLength_left  = filenameLength >> 8
    filenameLength_right = (filenameLength & 0xFF)

    output = bytearray([MagicNo_left, MagicNo_right, type, filenameLength_left, filenameLength_right]) +  byteFileName
    print("Success")
    return output

def main():
    IP, portNum, filename = getData() # gets and verifies that inputs are valid

    try:
        clientSock = socket.socket()

    except:
        print("Failed to build a socket")
        quitProgram()

    clientSock.settimeout(1.0) #gives the socket a 1seconds time limit

    try:
        # connect to the server
        clientSock.connect((IP, portNum))
    except:
        clientSock.close()
        print("Failed to connect with given server")
        quitProgram()


    requestFile = createByteFile(filename) #creates a request packet to send to server
    print("Sending request file to server...")
    try:
        clientSock.send(requestFile)
    except:
        print("An error occurs trying to send the file request to the server.")
        quitProgram()


    fullFile = bytearray() #creates a byte array awaiting to recieve the file back from server

    try:
        firstPacket = clientSock.recv(MAXBYTES)
    except socket.timeout:
        print("Socket Timeout Error: Could not recieve File Response")
        quitProgram()

    statusCode = firstPacket[3] #first finds the success of the given request
    if statusCode == 0:
        print("Error: The server was unable to retrieve \'" + str(filename) + "\' or it does not exist.")
        quitProgram()
    else:
        actualDataLength = (firstPacket[4] << 24) + (firstPacket[5] << 16) + (firstPacket[6] << 8) + firstPacket[7]
        bytesRecieved = len(firstPacket) - 8
        fullFile += firstPacket[8:]
        #checks that the recieved amount of bytes is same as the declared amount of bytes
        while bytesRecieved < actualDataLength:

            try:
                nextPacket = clientSock.recv(MAXBYTES)
            except socket.timeout:
                print("Socket Timeout Error: Could not recieve full File Response")
                quitProgram()

            fullFile += nextPacket
            bytesRecieved += len(nextPacket)


        if bytesRecieved == actualDataLength:
            print("File has been successful retrieved from the server.")
        else:
            print("An error has occurred while retrieving file from the server")
            quitProgram()

        print("Attempting to write file to \'" + str(filename) + "\'.")
        try:
            output = open(filename, "wb")
            output.write(fullFile)
        except:
            print("Error: Unable to write data to \'" + str(filename) + "\'.")
            quitProgram()

        print("File \'" + str(filename) + "\' was successfully transferred from server in "
              + str(bytesRecieved) + " bytes.")
        output.close()
        clientSock.close()
        quitProgram()

if __name__ == "__main__":
    main()