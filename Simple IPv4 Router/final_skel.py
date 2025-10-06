#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import RemoteController

class final_topo(Topo):
  """This class defines the network's physical topology."""
  def build(self):
    s1 = self.addSwitch('s1') 
    s2 = self.addSwitch('s2') 
    s3 = self.addSwitch('s3') 
    s4 = self.addSwitch('s4') 
    s5 = self.addSwitch('s5') 
    s6 = self.addSwitch('s6') 

    # Department A Hosts (Floor 1)
    h101 = self.addHost('h101', mac='00:00:00:00:01:01', ip='128.114.1.101/24', defaultRoute='h101-eth0')
    h102 = self.addHost('h102', mac='00:00:00:00:01:02', ip='128.114.1.102/24', defaultRoute='h102-eth0')
    h103 = self.addHost('h103', mac='00:00:00:00:01:03', ip='128.114.1.103/24', defaultRoute='h103-eth0')
    h104 = self.addHost('h104', mac='00:00:00:00:01:04', ip='128.114.1.104/24', defaultRoute='h104-eth0')

    h201 = self.addHost('h201', mac='00:00:00:00:02:01', ip='128.114.2.201/24', defaultRoute='h201-eth0')
    h202 = self.addHost('h202', mac='00:00:00:00:02:02', ip='128.114.2.202/24', defaultRoute='h202-eth0')
    h203 = self.addHost('h203', mac='00:00:00:00:02:03', ip='128.114.2.203/24', defaultRoute='h203-eth0')
    h204 = self.addHost('h204', mac='00:00:00:00:02:04', ip='128.114.2.204/24', defaultRoute='h204-eth0')

    h_trust = self.addHost('h_trust', mac='00:00:00:00:03:01', ip='192.47.38.109/24', defaultRoute='h_trust-eth0')
    h_untrust = self.addHost('h_untrust', mac='00:00:00:00:04:01', ip='108.35.24.113/24', defaultRoute='h_untrust-eth0')
    h_server = self.addHost('h_server', mac='00:00:00:00:05:01', ip='128.114.3.178/24', defaultRoute='h_server-eth0')

    self.addLink(s5, s1, port1=1, port2=1)
    self.addLink(s5, s2, port1=2, port2=1)
    self.addLink(s5, s3, port1=3, port2=1)
    self.addLink(s5, s4, port1=4, port2=1)
    self.addLink(s5, s6, port1=5, port2=1)
    self.addLink(s5, h_trust, port1=6, port2=0)
    self.addLink(s5, h_untrust, port1=7, port2=0)

    self.addLink(s1, h101, port1=2, port2=0)
    self.addLink(s1, h102, port1=3, port2=0)
    self.addLink(s2, h103, port1=2, port2=0)
    self.addLink(s2, h104, port1=3, port2=0)

    self.addLink(s3, h201, port1=2, port2=0)
    self.addLink(s3, h202, port1=3, port2=0)
    self.addLink(s4, h203, port1=2, port2=0)
    self.addLink(s4, h204, port1=3, port2=0)

    self.addLink(s6, h_server, port1=2, port2=0)

def configure():
  topo = final_topo()
  net = Mininet(topo=topo, controller=RemoteController)
  net.start()
  CLI(net)
  net.stop()

if __name__ == '__main__':
  configure()