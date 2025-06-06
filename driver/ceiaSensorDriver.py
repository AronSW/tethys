import socket
import time
import threading
import re
import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
from datetime import datetime





class CEIACWDDW_Driver:

    
    def __init__(self, ip='192.168.1.202', port=23, gateway=None, netmask=None, timeout=3):
        self.ip = ip
        self.port = port
        self.gateway = gateway
        self.netmask = netmask
        self.timeout = timeout
        self.sock = None

        self.running = False
        self.data_buffer = []
        self.listener_thread = None
        self.animation = None

        self.pin = "050899"
        self.prompt = ">"

        # Save data
        self.recording = False
        self.record_file = None
        self.record_writer = None


        # Live plot init
        self.plot_buffer_size = 100  # Show the last 100 points
        self.rh1_buffer = deque(maxlen=self.plot_buffer_size)
        self.rl1_buffer = deque(maxlen=self.plot_buffer_size)
        self.time_buffer = deque(maxlen=self.plot_buffer_size)  # Optional timestamp buffer
        self.plotting = False

    
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



    def parseSensorData(self, data_line, plot=True):
        
        pattern = r"\$MDA3,(\d+),(\d+),(\d+),(\d+),([NF]{1,2}),(\d+),([NSML])\*(\w+)"
        match = re.match(pattern, data_line)

        if not match:
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

        if plot:
            self.rh1_buffer.append(parsed_data["RH1"])
            self.rl1_buffer.append(parsed_data["RL1"])
            self.time_buffer.append(datetime.now())

        if self.recording and self.record_writer:
            self.record_writer.writerow([
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
        self.running = False
        if self.listener_thread:
            self.listener_thread.join()
        print("Data listener stopped.")

    def getBufferedData(self):
        
        return self.data_buffer
    

    def startRecording(self, filename):
        try:
            self.record_file = open(filename, mode='w', newline='')
            self.record_writer = csv.writer(self.record_file)
            self.record_writer.writerow([
                "Timestamp", "RH1", "RH1R", "RL1", "RL1R", "TYPE", "DIS", "DIM", "CHECKSUM"

            ])
            self.recording = True
            print(f"Recording started: {filename}")
        except Exception as e:
            print(f"ERROR, startRecording: {e}")

    def stopRecording(self):
        if self.recording:
            try:
                self.record_file.close()
                print("Recording stopped.")
            except Exception as e:
                print(f"ERROR stopRecording: {e}")
        self.recording = False
        self.record_file = None
        self.record_writer = None

    def startLivePlot(self):
        
        self.plotting = True
        fig, ax = plt.subplots()
        rh1_line, = ax.plot([], [], label="RH1", color="blue")
        rl1_line, = ax.plot([], [], label="RL1", color="red")

        ax.set_ylim(0, 10000)
        ax.set_xlim(0, self.plot_buffer_size)
        ax.legend()
        ax.set_title("Sensor Reading")
        ax.set_xlabel("Sample #")
        ax.set_ylabel("mV")

        def update(frame):
            if len(self.rh1_buffer) < 2:
                return rh1_line, rl1_line

            x = list(range(len(self.rh1_buffer)))
            rh1_line.set_data(x, list(self.rh1_buffer))
            rl1_line.set_data(x, list(self.rl1_buffer))

            ax.set_xlim(max(0, len(x) - self.plot_buffer_size), len(x))
            ax.set_ylim(
                min(min(self.rh1_buffer), min(self.rl1_buffer)) * 0.9,
                max(max(self.rh1_buffer), max(self.rl1_buffer)) * 1.1
            )

            return rh1_line, rl1_line

        self.animation = FuncAnimation(fig, update, interval=200, cache_frame_data=False)
        plt.tight_layout()
        plt.show()
        self.plotting = False

    
    def command_interface(driver):
        while True:
            cmd = input("Enter command (or 'exit'): ")
            if cmd.lower() == "exit":
                driver.stopDataListener()
                driver.stopContinuousOutput()
                driver.closeEthernet()
                print("Session ended.")
                break
            elif cmd.lower() == "live":
                driver.startLivePlot()
            elif cmd:
                parts = cmd.strip().split()
                if len(parts) == 1:
                    print("Response:", driver.sendCommand(parts[0]))
                elif len(parts) > 1:
                    print("Response:", driver.sendCommand(parts[0], " ".join(parts[1:])))


    
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
    





if __name__ == "__main__":
    metalDetectorDriver = CEIACWDDW_Driver()

    if not metalDetectorDriver.setupEthernet():
        print("Failed to establish connection.")
        exit()

    if not metalDetectorDriver.logIn():
        print("Failed to log in.")
        exit()

    metalDetectorDriver.startContinuousOutput()
    metalDetectorDriver.startDataListener()
    try:

        while True:
                cmd = input("Enter command (or 'exit'): ")
                if cmd.lower() == "exit":
                    metalDetectorDriver.stopDataListener()
                    metalDetectorDriver.stopContinuousOutput()
                    metalDetectorDriver.closeEthernet()
                    print("Session ended.")
                    break
                elif cmd.lower() == "live":
                    metalDetectorDriver.startLivePlot()
                    
                elif cmd.lower().startswith("record "):
                    _, filename = cmd.split(maxsplit=1)
                    metalDetectorDriver.startRecording(filename)
                elif cmd.lower() == "stoprecord":
                    metalDetectorDriver.stopRecording()
                elif cmd:
                    parts = cmd.strip().split()
                    query = parts[0]
                    data = " ".join(parts[1:]) if len(parts) > 1 else None
                    print("Response:", metalDetectorDriver.sendCommand(query, data))
    finally:    
        metalDetectorDriver.stopDataListener()
        metalDetectorDriver.closeEthernet()
