#define COLORS      3
#define CHANELS     6

#define RED         0
#define GREEN       1
#define BLUE        2

#define DDR_RED0    DDRD
#define DDR_GREEN0  DDRD
#define DDR_BLUE0   DDRD
#define DDR_RED1    DDRC
#define DDR_GREEN1  DDRC
#define DDR_BLUE1   DDRC
#define PORT_RED0   PORTD
#define PORT_GREEN0 PORTD
#define PORT_BLUE0  PORTD
#define PORT_RED1   PORTC
#define PORT_GREEN1 PORTC
#define PORT_BLUE1  PORTC
#define RED0        PD2
#define GREEN0      PD3
#define BLUE0       PD4
#define RED1        PC5
#define GREEN1      PC4
#define BLUE1       PC3

#include <util/delay.h>

uint8_t leds[COLORS][CHANELS];
uint8_t leds_buff[COLORS][CHANELS];
uint8_t counter = 0;

int main() {
    DDR_RED0   |= 1<<RED0;
    DDR_GREEN0 |= 1<<GREEN0;
    DDR_BLUE0  |= 1<<BLUE0;
    DDR_RED1   |= 1<<RED1;
    DDR_GREEN1 |= 1<<GREEN1;
    DDR_BLUE1  |= 1<<BLUE1;
    TCCR0B |= 1<<CS00;
    TIMSK0 |= 1<<TOIE0;
    sei();
    
    for (uint8_t i=0; i<COLORS; i++) {
        for (uint8_t j=0; j<CHANELS; j++) {
            leds[i][j] = 0;
            leds_buff[i][j] = 0;
        }
    }
    uint8_t temp = 1;
    while(1) {
        if (temp == 1) {
            if (leds[GREEN][0] < 255) {
                leds[GREEN][0]++;
                leds[RED][1]++;
            }
            else
                temp = 2;
        }
        if (temp == 2) {
            if (leds[RED][0] > 0) {
                leds[RED][0]--;
                leds[RED][1]--;
            }
            else
                temp = 3;
        }
        if (temp == 3) {
            if (leds[BLUE][0] < 255) {
                leds[BLUE][0]++;
                leds[GREEN][1]++;
            }
            else
                temp = 4;
        }
        if (temp == 4) {
            if (leds[GREEN][0] > 0) {
                leds[GREEN][0]--;
                leds[GREEN][1]--;
            }
            else
                temp = 5;
        }
        if (temp == 5) {
            if (leds[RED][0] < 255) {
                leds[RED][0]++;
                leds[BLUE][1]++;
            }
            else
                temp = 6;
        }
        if (temp == 6) {
            if (leds[BLUE][0] > 0) {
                leds[BLUE][0]--;
                leds[BLUE][1]--;
            }
            else
                temp = 1;
        }
        _delay_ms(2);
    }
}

ISR (TIMER0_OVF_vect) {
    counter++;
    if (counter == 0) {
        for (uint8_t i=0; i<COLORS; i++) {
            for (uint8_t j=0; j<CHANELS; j++) {
                leds_buff[i][j] = leds[i][j];
            }
        }
        PORT_RED0   &= ~(1<<RED0);
        PORT_RED1   &= ~(1<<RED1);
        PORT_GREEN0 &= ~(1<<GREEN0);
        PORT_GREEN1 &= ~(1<<GREEN1);
        PORT_BLUE0  &= ~(1<<BLUE0);
        PORT_BLUE1  &= ~(1<<BLUE1);
    }
    if (counter == leds_buff[RED][0])   PORT_RED0   |= 1<<RED0;
    if (counter == leds_buff[RED][1])   PORT_RED1   |= 1<<RED1;
    if (counter == leds_buff[GREEN][0]) PORT_GREEN0 |= 1<<GREEN0;
    if (counter == leds_buff[GREEN][1]) PORT_GREEN1 |= 1<<GREEN1;
    if (counter == leds_buff[BLUE][0])  PORT_BLUE0  |= 1<<BLUE0;
    if (counter == leds_buff[BLUE][1])  PORT_BLUE1  |= 1<<BLUE1;
}
