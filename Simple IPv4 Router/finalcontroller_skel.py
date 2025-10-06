from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr

log = core.getLogger()

IP_H_TRUST = IPAddr("192.47.38.109")
IP_H_UNTRUST = IPAddr("108.35.24.113")
IP_H_SERVER = IPAddr("128.114.3.178")

DEPT_A_IPS = [IPAddr("128.114.1.{0}".format(i)) for i in range(101, 105)]
DEPT_B_IPS = [IPAddr("128.114.2.{0}".format(i)) for i in range(201, 205)]

INTERNAL_IPS = DEPT_A_IPS + DEPT_B_IPS + [IP_H_SERVER]

class Final (object):
  def __init__ (self, connection):
    self.connection = connection
    connection.addListeners(self)

  def do_final (self, packet, packet_in, port_on_switch, switch_id):
    is_arp = packet.find('arp')
    is_ip = packet.find('ipv4')

    if is_ip:
        log.debug("Packet In: switch %s, src %s, dst %s", switch_id, is_ip.srcip, is_ip.dstip)

    if is_arp:
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        msg.data = packet_in
        self.connection.send(msg)
        return

    if not is_ip:
        return

    src_ip = is_ip.srcip
    dst_ip = is_ip.dstip
    is_icmp = packet.find('icmp')

    if src_ip == IP_H_UNTRUST and dst_ip == IP_H_SERVER:
        log.warning("FIREWALL: Dropping IP from Untrusted %s to Server %s", src_ip, dst_ip)
        msg = of.ofp_flow_mod(match=of.ofp_match.from_packet(packet))
        self.connection.send(msg)
        return

    if is_icmp and src_ip == IP_H_UNTRUST and dst_ip in INTERNAL_IPS:
        log.warning("FIREWALL: Dropping ICMP from Untrusted %s to Internal %s", src_ip, dst_ip)
        msg = of.ofp_flow_mod(match=of.ofp_match.from_packet(packet))
        self.connection.send(msg)
        return

    if src_ip == IP_H_TRUST and dst_ip == IP_H_SERVER:
        log.warning("FIREWALL: Dropping IP from Trusted %s to Server %s", src_ip, dst_ip)
        msg = of.ofp_flow_mod(match=of.ofp_match.from_packet(packet))
        self.connection.send(msg)
        return

    if is_icmp and src_ip == IP_H_TRUST and dst_ip in DEPT_B_IPS:
        log.warning("FIREWALL: Dropping ICMP from Trusted %s to Dept B %s", src_ip, dst_ip)
        msg = of.ofp_flow_mod(match=of.ofp_match.from_packet(packet))
        self.connection.send(msg)
        return

    if is_icmp and ((src_ip in DEPT_A_IPS and dst_ip in DEPT_B_IPS) or \
                   (src_ip in DEPT_B_IPS and dst_ip in DEPT_A_IPS)):
        log.warning("FIREWALL: Dropping ICMP between Dept A/B: %s -> %s", src_ip, dst_ip)
        msg = of.ofp_flow_mod(match=of.ofp_match.from_packet(packet))
        self.connection.send(msg)
        return

    out_port = None

    if switch_id == 5:
        if dst_ip in DEPT_A_IPS[:2]: out_port = 1
        elif dst_ip in DEPT_A_IPS[2:]: out_port = 2
        elif dst_ip in DEPT_B_IPS[:2]: out_port = 3
        elif dst_ip in DEPT_B_IPS[2:]: out_port = 4
        elif dst_ip == IP_H_SERVER: out_port = 5
        elif dst_ip == IP_H_TRUST: out_port = 6
        elif dst_ip == IP_H_UNTRUST: out_port = 7
    else:
        if (switch_id == 1 and dst_ip == IPAddr("128.114.1.101")): out_port = 2
        elif (switch_id == 1 and dst_ip == IPAddr("128.114.1.102")): out_port = 3
        elif (switch_id == 2 and dst_ip == IPAddr("128.114.1.103")): out_port = 2
        elif (switch_id == 2 and dst_ip == IPAddr("128.114.1.104")): out_port = 3
        elif (switch_id == 3 and dst_ip == IPAddr("128.114.2.201")): out_port = 2
        elif (switch_id == 3 and dst_ip == IPAddr("128.114.2.202")): out_port = 3
        elif (switch_id == 4 and dst_ip == IPAddr("128.114.2.203")): out_port = 2
        elif (switch_id == 4 and dst_ip == IPAddr("128.114.2.204")): out_port = 3
        elif (switch_id == 6 and dst_ip == IP_H_SERVER): out_port = 2
        else:
            out_port = 1

    if out_port is not None:
        log.info("ROUTING: Installing flow for sw %s, dst %s -> port %s", switch_id, dst_ip, out_port)
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port=out_port))
        msg.data = packet_in
        self.connection.send(msg)
    else:
        log.warning("ROUTING: No route found for %s from switch %s. Packet dropped.", dst_ip, switch_id)

  def _handle_PacketIn (self, event):
    packet = event.parsed
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return
    packet_in = event.ofp
    self.do_final(packet, packet_in, event.port, event.dpid)

def launch ():
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Final(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)