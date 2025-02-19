# from mininet.net import Mininet
# from mininet.topolib import TreeTopo
#
# tree4 = TreeTopo(depth=2,fanout=2)
# net = Mininet(topo=tree4)
# net.start()
# h1, h4  = net.hosts[0], net.hosts[3]
# print(f"h1.cmd('ping -c1 %s' % h4.IP()): {h1.cmd('ping -c1 %s' % h4.IP())}")
# net.stop()

"clusterperf.py compare the maximum throughput between SSH and GRE tunnels"

# from mininet.examples.cluster import RemoteSSHLink, RemoteGRELink, RemoteHost
# from mininet.net import Mininet
# from mininet.log import setLogLevel
#
# def perf(Link):
#     "Test connectivity nand performance over Link"
#     net = Mininet( host=RemoteHost, link=Link, waitConnected=True )
#     h1 = net.addHost( 'h1')
#     h2 = net.addHost( 'h2', server='ubuntu2' )
#     net.addLink( h1, h2 )
#     net.start()
#     net.pingAll()
#     net.iperf()
#     net.stop()
#
#
# if __name__ == '__main__':
#     setLogLevel('info')
#     perf( RemoteSSHLink )
#     perf( RemoteGRELink )

# !/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel


class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts."

    def build(self, n=2):
        switch = self.addSwitch('s1')
        # Python's range(N) generates 0..N-1
        for h in range(n):
            # host = self.addHost('h%s' % (h + 1))
            # host = self.addHost('h%s' % (h)) #starts with 0
            # host = self.addHost('gossip-statefulset-%s' % (h)) # Error: argument "gossip-statefulset-0-eth0" is wrong: "name" not a valid ifname
            host = self.addHost('gs%s' % (h))
            self.addLink(host, switch)


def simpleTest():
    "Create and test a simple network"
    topo = SingleSwitchTopo(n=4)
    net = Mininet(topo)
    net.start()
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    print("Testing network connectivity")
    net.pingAll()
    net.stop()


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
