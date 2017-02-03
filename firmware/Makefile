# Project name. Binary file will be name (TARG).hex
TARG = P3DA

# MCU type & frequency
MCU=atmega328p
F_CPU=16000000L

# Files in the project

SRCS = main.c

OBJS = $(SRCS:.c=.o)

CC = avr-gcc
OBJCOPY = avr-objcopy
SIZE = avr-size

# Flags for compiler
CFLAGS = -mmcu=$(MCU) -DF_CPU=$(F_CPU) -Wall -g -Os -lm  -mcall-prologues -std=c99
LDFLAGS = -mmcu=$(MCU) -Wall -g -Os

all: $(TARG)

$(TARG): $(OBJS)
	$(CC) $(LDFLAGS) -o $@.elf  $(OBJS) -lm
	$(OBJCOPY) -O ihex -R .eeprom -R .nwram  $@.elf $@.hex
	$(SIZE) -t $@.hex

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(SRCS:.c=.elf) $(TARG).elf $(OBJS)

prog:
	avrdude -carduino -P/dev/ttyUSB0 -p$(MCU) -b57600 -D -Uflash:w:$(TARG).hex:i
