#define RED         0
#define GREEN       1
#define BLUE        2

#define CATODE      0
#define ANODE       1

#define COLORS      3
#define CHANELS     6
#define COMMON      CATODE                  // Common electrode in RGB. CATODE or ANODE

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

uint8_t leds[COLORS][CHANELS];              // Values RGB LEDs. User change
uint8_t leds_buff[COLORS][CHANELS];         // Protected buffer RGB values. Program use only
uint8_t countPWM = 0;                       // Counter for software PWM

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
    TCCR0B |= 1<<CS00;                      // 1:1 F_T0
    TIMSK0 |= 1<<TOIE0;
}

int main() {
    Init();
    sei();

    leds[GREEN][0] = 0;
    leds[BLUE][0]  = 0;
    leds[RED][1]   = 0;
    leds[GREEN][1] = 0;
    leds[BLUE][1]  = 0;

    // Off inverted chanels
    leds[RED][2]   = 255;
    leds[GREEN][2] = 255;
    leds[BLUE][2]  = 255;
    leds[RED][3]   = 255;
    leds[GREEN][3] = 255;
    leds[BLUE][3]  = 255;
    leds[RED][4]   = 255;
    leds[GREEN][4] = 255;
    leds[BLUE][4]  = 255;
    leds[RED][5]   = 255;
    leds[GREEN][5] = 255;
    leds[BLUE][5]  = 255;

    while(1){
        while(++leds[RED][0]<255) {
            _delay_ms(3);
        }
        while(--leds[RED][0]>0) {
            _delay_ms(3);
        }
        _delay_ms(1000);
    }
}

ISR (TIMER0_OVF_vect) {
    if (++countPWM == 0) {
        for (uint8_t i=0; i<COLORS; i++) {
            for (uint8_t j=0; j<CHANELS; j++) {
                leds_buff[i][j] = leds[i][j];
            }
        }
        // Common anode or common catode
#if COMMON
        if (leds_buff[RED][0])     PORT_RED0   |= 1<<RED0;
        if (leds_buff[GREEN][0])   PORT_GREEN0 |= 1<<GREEN0;
        if (leds_buff[BLUE][0])    PORT_BLUE0  |= 1<<BLUE0;
        if (leds_buff[RED][1])     PORT_RED1   |= 1<<RED1;
        if (leds_buff[GREEN][1])   PORT_GREEN1 |= 1<<GREEN1;
        if (leds_buff[BLUE][1])    PORT_BLUE1  |= 1<<BLUE1;
        if (leds_buff[RED][2])     PORT_RED2   |= 1<<RED2;
        if (leds_buff[GREEN][2])   PORT_GREEN2 |= 1<<GREEN2;
        if (leds_buff[BLUE][2])    PORT_BLUE2  |= 1<<BLUE2;
        if (leds_buff[RED][3])     PORT_RED3   |= 1<<RED3;
        if (leds_buff[GREEN][3])   PORT_GREEN3 |= 1<<GREEN3;
        if (leds_buff[BLUE][3])    PORT_BLUE3  |= 1<<BLUE3;
        if (leds_buff[RED][4])     PORT_RED4   |= 1<<RED4;
        if (leds_buff[GREEN][4])   PORT_GREEN4 |= 1<<GREEN4;
        if (leds_buff[BLUE][4])    PORT_BLUE4  |= 1<<BLUE4;
        if (leds_buff[RED][5])     PORT_RED5   |= 1<<RED5;
        if (leds_buff[GREEN][5])   PORT_GREEN5 |= 1<<GREEN5;
        if (leds_buff[BLUE][5])    PORT_BLUE5  |= 1<<BLUE5;
#else
        if (leds_buff[RED][0])     PORT_RED0   &= ~(1<<RED0);
        if (leds_buff[GREEN][0])   PORT_GREEN0 &= ~(1<<GREEN0);
        if (leds_buff[BLUE][0])    PORT_BLUE0  &= ~(1<<BLUE0);
        if (leds_buff[RED][1])     PORT_RED1   &= ~(1<<RED1);
        if (leds_buff[GREEN][1])   PORT_GREEN1 &= ~(1<<GREEN1);
        if (leds_buff[BLUE][1])    PORT_BLUE1  &= ~(1<<BLUE1);
        if (leds_buff[RED][2])     PORT_RED2   &= ~(1<<RED2);
        if (leds_buff[GREEN][2])   PORT_GREEN2 &= ~(1<<GREEN2);
        if (leds_buff[BLUE][2])    PORT_BLUE2  &= ~(1<<BLUE2);
        if (leds_buff[RED][3])     PORT_RED3   &= ~(1<<RED3);
        if (leds_buff[GREEN][3])   PORT_GREEN3 &= ~(1<<GREEN3);
        if (leds_buff[BLUE][3])    PORT_BLUE3  &= ~(1<<BLUE3);
        if (leds_buff[RED][4])     PORT_RED4   &= ~(1<<RED4);
        if (leds_buff[GREEN][4])   PORT_GREEN4 &= ~(1<<GREEN4);
        if (leds_buff[BLUE][4])    PORT_BLUE4  &= ~(1<<BLUE4);
        if (leds_buff[RED][5])     PORT_RED5   &= ~(1<<RED5);
        if (leds_buff[GREEN][5])   PORT_GREEN5 &= ~(1<<GREEN5);
        if (leds_buff[BLUE][5])    PORT_BLUE5  &= ~(1<<BLUE5);
#endif
    }
#if COMMON
    if (leds_buff[RED][0]   == countPWM)    PORT_RED0   &= ~(1<<RED0);
    if (leds_buff[GREEN][0] == countPWM)    PORT_GREEN0 &= ~(1<<GREEN0);
    if (leds_buff[BLUE][0]  == countPWM)    PORT_BLUE0  &= ~(1<<BLUE0);
    if (leds_buff[RED][1]   == countPWM)    PORT_RED1   &= ~(1<<RED1);
    if (leds_buff[GREEN][1] == countPWM)    PORT_GREEN1 &= ~(1<<GREEN1);
    if (leds_buff[BLUE][1]  == countPWM)    PORT_BLUE1  &= ~(1<<BLUE1);
    if (leds_buff[RED][2]   == countPWM)    PORT_RED2   &= ~(1<<RED2);
    if (leds_buff[GREEN][2] == countPWM)    PORT_GREEN2 &= ~(1<<GREEN2);
    if (leds_buff[BLUE][2]  == countPWM)    PORT_BLUE2  &= ~(1<<BLUE2);
    if (leds_buff[RED][3]   == countPWM)    PORT_RED3   &= ~(1<<RED3);
    if (leds_buff[GREEN][3] == countPWM)    PORT_GREEN3 &= ~(1<<GREEN3);
    if (leds_buff[BLUE][3]  == countPWM)    PORT_BLUE3  &= ~(1<<BLUE3);
    if (leds_buff[RED][4]   == countPWM)    PORT_RED4   &= ~(1<<RED4);
    if (leds_buff[GREEN][4] == countPWM)    PORT_GREEN4 &= ~(1<<GREEN4);
    if (leds_buff[BLUE][4]  == countPWM)    PORT_BLUE4  &= ~(1<<BLUE4);
    if (leds_buff[RED][5]   == countPWM)    PORT_RED5   &= ~(1<<RED5);
    if (leds_buff[GREEN][5] == countPWM)    PORT_GREEN5 &= ~(1<<GREEN5);
    if (leds_buff[BLUE][5]  == countPWM)    PORT_BLUE5  &= ~(1<<BLUE5);
#else
    if (leds_buff[RED][0]   == countPWM)    PORT_RED0   |= 1<<RED0;
    if (leds_buff[GREEN][0] == countPWM)    PORT_GREEN0 |= 1<<GREEN0;
    if (leds_buff[BLUE][0]  == countPWM)    PORT_BLUE0  |= 1<<BLUE0;
    if (leds_buff[RED][1]   == countPWM)    PORT_RED1   |= 1<<RED1;
    if (leds_buff[GREEN][1] == countPWM)    PORT_GREEN1 |= 1<<GREEN1;
    if (leds_buff[BLUE][1]  == countPWM)    PORT_BLUE1  |= 1<<BLUE1;
    if (leds_buff[RED][2]   == countPWM)    PORT_RED2   |= 1<<RED2;
    if (leds_buff[GREEN][2] == countPWM)    PORT_GREEN2 |= 1<<GREEN2;
    if (leds_buff[BLUE][2]  == countPWM)    PORT_BLUE2  |= 1<<BLUE2;
    if (leds_buff[RED][3]   == countPWM)    PORT_RED3   |= 1<<RED3;
    if (leds_buff[GREEN][3] == countPWM)    PORT_GREEN3 |= 1<<GREEN3;
    if (leds_buff[BLUE][3]  == countPWM)    PORT_BLUE3  |= 1<<BLUE3;
    if (leds_buff[RED][4]   == countPWM)    PORT_RED4   |= 1<<RED4;
    if (leds_buff[GREEN][4] == countPWM)    PORT_GREEN4 |= 1<<GREEN4;
    if (leds_buff[BLUE][4]  == countPWM)    PORT_BLUE4  |= 1<<BLUE4;
    if (leds_buff[RED][5]   == countPWM)    PORT_RED5   |= 1<<RED5;
    if (leds_buff[GREEN][5] == countPWM)    PORT_GREEN5 |= 1<<GREEN5;
    if (leds_buff[BLUE][5]  == countPWM)    PORT_BLUE5  |= 1<<BLUE5;
#endif
}