import socket
import time
import threading
import re
import csv
import serial
from datetime import datetime




class CEIACWDDW_Driver:

    
    def __init__(self, ip='192.168.1.202', port=23, gateway=None, netmask=None, timeout=3, csv_file='sensor_data.csv'):
        self.ip = ip
        self.port = port
        self.gateway = gateway
        self.netmask = netmask
        self.timeout = timeout
        self.sock = None

        self.running = False
        self.data_buffer = []
        self.listener_thread = None
        self.csv_file = csv_file

        self.pin = "050899"
        self.prompt = ">"

        with open(self.csv_file, mode = 'w', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Timestamp", "RH1", "RH1R", "RL1", "RL1R", "Ferrous", "Distance", "Size", "Checksum"
            ])
    
    def setupEthernet(self):
        """Opens Ethernet socket."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.ip, self.port))
            print(f"SetupEth: Connected to sensor at {self.ip}:{self.port}")
            return True
        except socket.timeout:
            print(f"ERROR SetupEth: Connection to {self.ip}:{self.port} timed out.")
        except socket.error as e:
            print(f"ERROR SetupEth: {e}")
            return False

    def closeEthernet(self):
        """Closes Ethernet socket."""
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                print(f"Connection to {self.ip}:{self.port} is closed.")
            except socket.error as e:
                print(f"ERROR CloseEth: {e}")
            finally:
                self.sock = None    

    def sendCommand(self, query, data=None):
        
        if data == None:
            command = query + "\r"
        else:
            command = f"{query} {data}\r"

        
        self.sock.sendall(command.encode())

        buffer_size = 50

        try:
        # Receiving streamed data from the socket
            response = self.sock.recv(buffer_size).decode()
            if response == ">":
                response = None
            elif ">" in response:
                response = response.split(">")[0]
                print(f"{response}")

            response = response.strip()
            
            return response

        except socket.timeout:
            print(f"ERROR queryResponse: Timed out.")
        except socket.error as e:
            print(f"ERROR queryResponse: {e}")
        return None
    
    def logIn(self):
        print(f"Logging in to sensor...")
        response = self.sendCommand(self.pin)

        if response is not None:
            print(f"Login succesful")
            return True
        else:
            print (f"ERROR logIn: expected prompt not received.")


    def saveToCSV(self, parsed_data):
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                parsed_data["Timestamp"],
                parsed_data["RH1"],
                parsed_data["RH1R"],
                parsed_data["RL1"],
                parsed_data["RL1R"],
                parsed_data["TYPE"],
                parsed_data["DIS"],
                parsed_data["DIM"],
                parsed_data["CHECKSUM"]
            ])


    def parseSensorData(self, data_line):
        
        pattern = r"\$MDA3,(\d+),(\d+),(\d+),(\d+),([NF]{1,2}),(\d+),([NSML])\*(\w+)"
        match = re.match(pattern, data_line)

        if not match:
            print(f"ERROR parseSensorData: Format not recognised {data_line}")
            return None
        rh1, rh1r, rl1, rl1r, dtype, dis, dim, checksum = match.groups()

        parsed_data = {
            "Timestamp": datetime.now().isoformat(),
            "RH1": int(rh1),
            "RH1R": int(rh1r),
            "RL1": int(rl1),
            "RL1R": int(rl1r),
            "TYPE": dtype,
            "DIS": int(dis),
            "DIM": dim,
            "CHECKSUM": checksum
        }

        self.saveToCSV(parsed_data)
        return parsed_data

    def startDataListener(self, callback=None):
        
        if not self.sock:
            print("ERROR startListener")
            return
        self.running = True
        
        def listen():
            while self.running:
                try:
                    
                    #Recieve data
                    data = self.sock.recv(200).decode()
                    if data:
                        #Split data in lines if needed
                        lines = data.split("\r")
                        
                        for line in lines:
                            # Ignore command returns
                            if not line.startswith("$MDA3"):
                                continue
                            if line.strip():
                                # Parse data and add to the data buffer.
                                self.data_buffer.append(self.parseSensorData(line))
                                if callback:
                                    callback(line.strip())
                except socket.timeout:
                    pass
                except Exception as e:
                    print(f"ERROR Listener: {e}")        
                    self.running = False
        self.listener_thread = threading.Thread(target=listen, daemon = True)
        self.listener_thread.start()

    def stopDataListener(self):
        """
        Stops the data listener.
        """
        print("Stopping data listener...")
        self.running = False
        if self.listener_thread:
            self.listener_thread.join()
        print("Data listener stopped.")

    def getBufferedData(self):
        """
        Returns the list of buffered data lines.
        """
        return self.data_buffer

    
    """---------------------------   Commands   ---------------------------"""
    def sendEndOfProgrammingMode(self):
        response = self.sendCommand("PE")
        return response
    
    def readParameterList(self):
        response = self.sendCommand("PT")
        return response
    
    def sendResetCommand(self):
        response = self.sendCommand("RE")
        return response
    
    def readSerialNumber(self):
        response = self.sendCommand("SN")
        return response
    
    def sensitivity(self, data = None): 
        response = self.sendCommand("SE", data)
        return response

    def readStatus(self):
        response = self.sendCommand("STA")
        return response
    
    def readWorkingTime(self):
        response = self.sendCommand("WT")
        return response
    
    def readProgramVersion(self):
        response = self.sendCommand("PV")
        return response
    
    def ipAddress(self, data = None):
        response = self.sendCommand("IPA", data)
        return response
    
    def gatewayAddress(self, data = None):
        response = self.sendCommand("GW", data)
        return response
    
    def subnetMask(self, data = None):
        response = self.sendCommand("MASK", data)
        return response
    
    def serverPort(self, data = None):
        response = self.sendCommand("SPT", data)
        return response
    
    def selfCheck(self):
        response = self.sendCommand("SC")
        return response
    
    def waterType(self, water_type = None):
        if water_type == 1:
            response = self.sendCommand("WTY FS")
        elif water_type == 2:
            response = self.sendCommand("WTY SW")
        else:
            response = self.sendCommand("WTY")
        return response
    
    def startContinuousOutput(self):
        response = self.sendCommand("CO ON")
        return response
    
    def stopContinuousOutput(self):
        response = self.sendCommand("CO OFF")
        return response   

    def outputRate(self, data = None):
        response = self.sendCommand("COR", data)
        return response
    
    """-------------------------   Commands end   -------------------------"""
    



    def driverTest(self):
        """
        Runs through all sensor functionality to validate operation.
        """
        print("Starting full sensor test...")

        if not self.setupEthernet():
            print("Failed to establish connection.")
            return
        
        if not self.logIn():
            print("Failed to log in.")
            self.closeEthernet()
            return
        

        print("\n--- Configuring Sensor ---")
        print("Setting sensitivity to 127...")
        print("Response:", self.sensitivity(127))

        print("Setting output rate to 10Hz...")
        print("Response:", self.outputRate(10))

        # print("Ending programming mode...")
        # print("Response:", self.sendEndOfProgrammingMode())

 
        print("Resetting sensor...")
        print("Response:", self.sendResetCommand())

        
        print("\n--- Configuring Network ---")
        print("Setting IP Address...")
        print("Response:", self.ipAddress())
        
        print("Setting Gateway Address...")
        print("Response:", self.gatewayAddress())
        
        print("Setting Subnet Mask...")
        print("Response:", self.subnetMask())

        print("Setting Server Port...")
        print("Response:", self.serverPort())


        print("\n--- Reading Sensor Status and Info ---")
        print("Sensor Status:", self.readStatus())
        print("Working Time:", self.readWorkingTime())
        print("Program Version:", self.readProgramVersion())
        print("Serial Number:", self.readSerialNumber())
        print("Self Check:", self.selfCheck())

        
        print("\n--- Starting Continuous Output ---")
        self.startContinuousOutput()

        print("\n--- Starting Data Listener ---")
        self.startDataListener()
        time.sleep(2) 
        self.stopDataListener()

        print("\n--- Buffered Data ---")
        for line in self.getBufferedData():
            print(line)

        print("\n--- Stopping Continuous Output ---")
        self.stoppContinuousOutput()

        print("\n--- Closing Connection ---")
        self.closeEthernet()
        print("Sensor test completed successfully.")

def sensorTest(sensitivity, test_name, rate, test_duration = None):
    
    timestamp = datetime.now().strftime("%d%m%y_%H%M")
    csv_filename = f"sensor_data_test_{test_name}_{timestamp}.csv"
    print(f"Data saved to {csv_filename}")

    metalDetectorDriver = CEIACWDDW_Driver(csv_file=csv_filename)

    if not metalDetectorDriver.setupEthernet():
            print("Failed to establish connection.")
            return
        
    
    if not metalDetectorDriver.logIn():
            print("Failed to log in.")
            metalDetectorDriver.closeEthernet()
            return
    
    metalDetectorDriver.sendResetCommand()
    time.sleep(5)

    selfCheckResponse = metalDetectorDriver.selfCheck()
    if selfCheckResponse != "SC OK":
        print(f"Self check failed with {selfCheckResponse}")
        metalDetectorDriver.closeEthernet()
        return

    status_response = metalDetectorDriver.readStatus()
    retry_attempts = 30
    while status_response == "STA 4" and retry_attempts > 0:
        print("Status is '4'. Waiting 1 second and retrying...")
        time.sleep(1)
        status_response = metalDetectorDriver.readStatus()
        retry_attempts -= 1

    if status_response == "STA 64":
        print(f"ERROR: Status returned '64'. Critical error, closing connection.")
        metalDetectorDriver.closeEthernet()
        return
    elif status_response == "STA 1":
        print(f"Alarm above threshold.")
        

    
    metalDetectorDriver.sensitivity(sensitivity)
    metalDetectorDriver.outputRate(rate)
  
    metalDetectorDriver.startContinuousOutput()
    metalDetectorDriver.startDataListener()
    

    if test_duration == None:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping test.")
    else:
        time.sleep(test_duration)
            
    metalDetectorDriver.stopDataListener()
    metalDetectorDriver.stopContinuousOutput()
    metalDetectorDriver.closeEthernet()
    print(f"Data successfully saved to '{csv_filename}'.")

def constantThrusterTest(sensitivity, test_name, rate, thruster_value, test_duration = None):
    
    arduino_port = "COM7"
    baud_rate = 9600
    timeout = 1

    ser = serial.Serial(arduino_port, baud_rate, timeout=timeout)
    time.sleep(2)

    ser.write(b"0\n")

    timestamp = datetime.now().strftime("%d%m%y_%H%M")
    csv_filename = f"thruster_test_{test_name}_{timestamp}.csv"
    print(f"Data saved to {csv_filename}")

    metalDetectorDriver = CEIACWDDW_Driver(csv_file=csv_filename)

    if not metalDetectorDriver.setupEthernet():
            print("Failed to establish connection.")
            return
        
    
    if not metalDetectorDriver.logIn():
            print("Failed to log in.")
            metalDetectorDriver.closeEthernet()
            return
    
    metalDetectorDriver.sendResetCommand()
    time.sleep(5)

    selfCheckResponse = metalDetectorDriver.selfCheck()
    if selfCheckResponse != "SC OK":
        print(f"Self check failed with {selfCheckResponse}")
        metalDetectorDriver.closeEthernet()
        return

    status_response = metalDetectorDriver.readStatus()
    retry_attempts = 30
    while status_response == "STA 4" and retry_attempts > 0:
        print("Status is '4'. Waiting 1 second and retrying...")
        time.sleep(1)
        status_response = metalDetectorDriver.readStatus()
        retry_attempts -= 1

    if status_response == "STA 64":
        print(f"ERROR: Status returned '64'. Critical error, closing connection.")
        metalDetectorDriver.closeEthernet()
        return
    elif status_response == "STA 1":
        print(f"Alarm above threshold.")
        
    
    metalDetectorDriver.sensitivity(sensitivity)
    metalDetectorDriver.outputRate(rate)

    ser.write(thruster_value)
    time.sleep(1)

    metalDetectorDriver.startContinuousOutput()
    metalDetectorDriver.startDataListener()
    time.sleep(test_duration)

    metalDetectorDriver.stopDataListener()
    metalDetectorDriver.stopContinuousOutput()
    metalDetectorDriver.closeEthernet()
    ser.write(thruster_value)
    print(f"Data successfully saved to '{csv_filename}'.")




#   Default test values, 127, "TestName", 50, 5
sensorTest(127, "SSide20dm", 50, 5)

#   Default test values, 127, "TestName", 50, thrustervalue [-100, 100], 5
constantThrusterTest(127, "ThrusterTestBaseline", 50, 0, 5)


  
