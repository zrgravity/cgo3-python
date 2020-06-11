#include <SoftwareSerial.h>
#include <Arduino.h>

#include "checksum.h"
//#include <SoftwareSerial.h>
//#include <Arduino.h>
#include <dummy.h>

#define PACKET_SEQ_LOC 2
#define K1_LOC_BYTE1 22
#define SL1_LOC_BYTE1 24
#define S1_LOC_BYTE1 26
#define S2_LOC_BYTE1 28

#define CGO3_RX_PIN 32
#define CGO3_TX_PIN 33

uint8_t initpacket[]={0xFE,0x03,0x00,0x01,0x00,0x00,0x00,0x01,0x02,0x00,0x01,0x00,0x00};
uint8_t outputmsg[]={0xFE,0x1A,0x00,0x01,0x00,0x02,0x00,0x01,0x9D,0x0A,0xE6,0xFF,0xFD,0xFF,0x97,0x25,0x1F,0x00,0x01,0x00,0x00,0x00,0x02,0x08,0x56,0x0D,0x00,0x08,0xAB,0x02,0x88,0x08,0xF4,0x01,0x00,0x00};
uint8_t packet_seq = 0;
uint8_t k1_command[2];
uint8_t sl1_command[2];
uint8_t s1_command[2];
uint8_t s2_command[2];

SoftwareSerial CGO3Serial(CGO3_RX_PIN,CGO3_TX_PIN, false);

void setup() {
  // put your setup code here, to run once:
  uint8_t k;
  Serial.begin(115200);
  CGO3Serial.begin(115200);
  delay(100);
  while (CGO3Serial.available()<1) {
    for (int i=0;i<5;i=i+1) {
      updatemsg(initpacket);
      Serial.println(".");
      CGO3Serial.write(initpacket,13);   
    }
  }
  s1_command[0]=0x00;
  s1_command[1]=0x08;
  s2_command[0]=0x00;
  s2_command[1]=0x08;
  sl1_command[0]=0x00;
  sl1_command[1]=0x08;
  k1_command[0]=0x00;
  k1_command[1]=0x08;
}

void loop() {
  uint8_t k;
  char t;
  if (Serial.available() > 0) {
    t=Serial.read();
    switch (t) {
      case 'c':
        sl1_command[0]=0x02;
        sl1_command[1]=0x08;
        break;
      case 'u':
        sl1_command[0]=0xAB;
        sl1_command[1]=0x02;
        break;
      case 'd':
        sl1_command[0]=0x56;
        sl1_command[1]=0x0d;
        break; 
       case 'm':
        k1_command[0]=0x02;
        k1_command[1]=0x08;
        break;
      case 'r':
        k1_command[0]=0xAB;
        k1_command[1]=0x02;
        break;
      case 'l':
        k1_command[0]=0x56;
        k1_command[1]=0x0d;
        break;
      case 'a':
        s1_command[0]=0xAB;
        s1_command[1]=0x02;
        break;
      case 'v':
        s1_command[0]=0x54;
        s1_command[1]=0x0D;
        break;
      case 'f':
        s2_command[0]=0xAB;
        s2_command[1]=0x02;
        break;
      case 'g':
        s2_command[0]=0x54;
        s2_command[1]=0x0D;
        break;
    }
  }
  updatemsg(outputmsg);
  CGO3Serial.write(outputmsg,outputmsg[1]+10);

}

void updatemsg(uint8_t* msgptr) {
  uint8_t c;
  uint16_t tempchecksum;

  msgptr[PACKET_SEQ_LOC]=packet_seq;
  if (msgptr[1]==0x1A) {
    msgptr[K1_LOC_BYTE1]=k1_command[0];
    msgptr[K1_LOC_BYTE1+1]=k1_command[1];
    msgptr[SL1_LOC_BYTE1]=sl1_command[0];
    msgptr[SL1_LOC_BYTE1+1]=sl1_command[1];
    msgptr[S1_LOC_BYTE1]=s1_command[0];
    msgptr[S1_LOC_BYTE1+1]=s1_command[1];
    msgptr[S2_LOC_BYTE1]=s2_command[0];
    msgptr[S2_LOC_BYTE1+1]=s2_command[1];
  }
  crc_init(&tempchecksum);
  //length from packet + 10 header bytes - CRC
  for (uint8_t j=1;j<msgptr[1]+8;j=j+1) {
    crc_accumulate(msgptr[j],&tempchecksum);
  }
  //add the CRC_EXTRA Byte which seems to be 0
  crc_accumulate(0,&tempchecksum);
  msgptr[msgptr[1]+8]=tempchecksum & 0x00FF;
  msgptr[msgptr[1]+9]=((tempchecksum >> 8)&0x00FF);
  if (packet_seq==255) {
    packet_seq=0;
  } else {
    packet_seq=packet_seq+1;
  }
}