#define COLORS      3
#define CHANELS     6

#define RED         0
#define GREEN       1
#define BLUE        2

/*@{*/ // Ports setup
#define DDR_RED0    DDRD
#define DDR_GREEN0  DDRD
#define DDR_BLUE0   DDRD
#define DDR_RED1    DDRC
#define DDR_GREEN1  DDRC
#define DDR_BLUE1   DDRC
#define DDR_RED2    DDRB
#define DDR_GREEN2  DDRB
#define DDR_BLUE2   DDRB
#define DDR_RED3    DDRB
#define DDR_GREEN3  DDRB
#define DDR_BLUE3   DDRB
#define DDR_RED4    DDRB
#define DDR_GREEN4  DDRB
#define DDR_BLUE4   DDRB
#define DDR_RED5    DDRB
#define DDR_GREEN5  DDRB
#define DDR_BLUE5   DDRB

#define PORT_RED0   PORTD
#define PORT_GREEN0 PORTD
#define PORT_BLUE0  PORTD
#define PORT_RED1   PORTC
#define PORT_GREEN1 PORTC
#define PORT_BLUE1  PORTC
#define PORT_RED2   PORTB
#define PORT_GREEN2 PORTB
#define PORT_BLUE2  PORTB
#define PORT_RED3   PORTB
#define PORT_GREEN3 PORTB
#define PORT_BLUE3  PORTB
#define PORT_RED4   PORTB
#define PORT_GREEN4 PORTB
#define PORT_BLUE4  PORTB
#define PORT_RED5   PORTB
#define PORT_GREEN5 PORTB
#define PORT_BLUE5  PORTB

#define RED0        PD2
#define GREEN0      PD3
#define BLUE0       PD4
#define RED1        PC5
#define GREEN1      PC4
#define BLUE1       PC3
#define RED2        PB5
#define GREEN2      PB5
#define BLUE2       PB5
#define RED3        PB5
#define GREEN3      PB5
#define BLUE3       PB5
#define RED4        PB5
#define GREEN4      PB5
#define BLUE4       PB5
#define RED5        PB5
#define GREEN5      PB5
#define BLUE5       PB5
/*@}*/

#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>

inline void InitPorts() {
    DDR_RED0 |= 1<<RED0;
    DDR_RED1 |= 1<<RED1;
    DDR_RED2 |= 1<<RED2;
    DDR_RED3 |= 1<<RED3;
    DDR_RED4 |= 1<<RED4;
    DDR_RED5 |= 1<<RED5;
    DDR_GREEN0 |= 1<<GREEN0;
    DDR_GREEN1 |= 1<<GREEN1;
    DDR_GREEN2 |= 1<<GREEN2;
    DDR_GREEN3 |= 1<<GREEN3;
    DDR_GREEN4 |= 1<<GREEN4;
    DDR_GREEN5 |= 1<<GREEN5;
    DDR_BLUE0 |= 1<<BLUE0;
    DDR_BLUE1 |= 1<<BLUE1;
    DDR_BLUE2 |= 1<<BLUE2;
    DDR_BLUE3 |= 1<<BLUE3;
    DDR_BLUE4 |= 1<<BLUE4;
    DDR_BLUE5 |= 1<<BLUE5;
}

void Init() {
    InitPorts();
}

int main() {
    Init();
    while(1){
        _delay_ms(10);
    }
}