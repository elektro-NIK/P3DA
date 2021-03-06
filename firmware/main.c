/*@{*/ // Ports setup
#define DDR_RED0    DDRD
#define DDR_GREEN0  DDRD
#define DDR_BLUE0   DDRD
#define DDR_RED1    DDRD
#define DDR_GREEN1  DDRD
#define DDR_BLUE1   DDRD
#define DDR_RED2    DDRB
#define DDR_GREEN2  DDRB
#define DDR_BLUE2   DDRB
#define DDR_RED3    DDRB
#define DDR_GREEN3  DDRB
#define DDR_BLUE3   DDRB
#define DDR_RED4    DDRC
#define DDR_GREEN4  DDRC
#define DDR_BLUE4   DDRC
#define DDR_RED5    DDRC
#define DDR_GREEN5  DDRC
#define DDR_BLUE5   DDRC

#define PORT_RED0   PORTD
#define PORT_GREEN0 PORTD
#define PORT_BLUE0  PORTD
#define PORT_RED1   PORTD
#define PORT_GREEN1 PORTD
#define PORT_BLUE1  PORTD
#define PORT_RED2   PORTB
#define PORT_GREEN2 PORTB
#define PORT_BLUE2  PORTB
#define PORT_RED3   PORTB
#define PORT_GREEN3 PORTB
#define PORT_BLUE3  PORTB
#define PORT_RED4   PORTC
#define PORT_GREEN4 PORTC
#define PORT_BLUE4  PORTC
#define PORT_RED5   PORTC
#define PORT_GREEN5 PORTC
#define PORT_BLUE5  PORTC

#define RED0        PD3
#define GREEN0      PD4
#define BLUE0       PD2
#define RED1        PD6
#define GREEN1      PD7
#define BLUE1       PD5
#define RED2        PB1
#define GREEN2      PB2
#define BLUE2       PB0
#define RED3        PB3
#define GREEN3      PB5
#define BLUE3       PB4
#define RED4        PC1
#define GREEN4      PC2
#define BLUE4       PC0
#define RED5        PC4
#define GREEN5      PC5
#define BLUE5       PC3
/*@}*/

/*@{*/ // LEDs setup
#define RED         0
#define GREEN       1
#define BLUE        2
#define CATHODE     0
#define ANODE       1

#define COLORS      3
#define CHANELS     6
#define COMMON      CATHODE                 // Common electrode in RGB. CATHODE or ANODE
/*@}*/

/*@{*/ // PWM setup
#define PWMDEPTH    9
#define MAXPWM      511                 // (2^PWMDEPTH) - 1
/*@}*/

/*@{*/ // USART setup
#define BAUD 38400

#define USART_RX_BUFFER_SIZE 128            // 2,4,8,16,32,64,128 or 256 bytes
#define USART_TX_BUFFER_SIZE 128            // 2,4,8,16,32,64,128 or 256 bytes
#define USART_RX_BUFFER_MASK (USART_RX_BUFFER_SIZE - 1)
#define USART_TX_BUFFER_MASK (USART_TX_BUFFER_SIZE - 1)

#if (USART_RX_BUFFER_SIZE & USART_RX_BUFFER_MASK)
#error RX buffer size is not a power of 2
#endif
#if (USART_TX_BUFFER_SIZE & USART_TX_BUFFER_MASK)
#error TX buffer size is not a power of 2
#endif
/*@}*/

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/setbaud.h>

/*@{*/ // Global variables
static uint8_t USART_RxBuf[USART_RX_BUFFER_SIZE];
static volatile uint8_t USART_RxHead;
static volatile uint8_t USART_RxTail;
static uint8_t USART_TxBuf[USART_TX_BUFFER_SIZE];
static volatile uint8_t USART_TxHead;
static volatile uint8_t USART_TxTail;

volatile uint16_t leds[COLORS][CHANELS];              // Values RGB LEDs. User changeble
uint16_t leds_buff[COLORS][CHANELS];         // Protected buffer RGB values. Program use only
volatile uint16_t countPWM = 0;                       // Counter for software PWM
/*@}*/

/*@{*/ // Functions section

void InitPorts() {
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

void USART0_Init() {
    UBRR0H = UBRRH_VALUE;
    UBRR0L = UBRRL_VALUE;
    #if USE_2X
    UCSR0A |= 1<<U2X0;
    #else
    UCSR0A &= ~(1<<U2X0);
    #endif
    UCSR0B |= 1<<RXEN0 | 1<<TXEN0 | 1<<RXCIE0;                      // Enable RX & TX, enable interrupt for end of RX
    USART_RxTail = 0;
    USART_RxHead = 0;
    USART_TxTail = 0;
    USART_TxHead = 0;
}

void Init() {
    InitPorts();
    TCCR0B |= 1<<CS01;                      // F_T0 = F_CPU / 8
    TIMSK0 |= 1<<TOIE0;
    USART0_Init();
}

uint8_t USART0_Receive() {
    uint8_t tmptail;
    while (USART_RxHead == USART_RxTail) {}                         // Wait for incomming data
    tmptail = (USART_RxTail + 1) & USART_RX_BUFFER_MASK;        // Calculate buffer index
    USART_RxTail = tmptail;                                     // Store new index
    return USART_RxBuf[tmptail];
}

void USART0_Transmit (uint8_t data) {
    uint8_t tmphead;
    tmphead = (USART_TxHead + 1) & USART_TX_BUFFER_MASK;            // Calculate buffer index
    while (tmphead == USART_TxTail) {}                              // Wait for free space in buffer
    USART_TxBuf[tmphead] = data;
    USART_TxHead = tmphead;                                         // Store new index
    UCSR0B |= 1<<UDRIE0;
}

uint8_t DataInReceiveBuffer() {
    return (USART_RxHead != USART_RxTail);                          // Return 0 (FALSE) if the receive buffer is empty
}

uint8_t hex2int(uint8_t hex) {
    if (hex >= '0' && hex <= '9') return hex -'0';
    else if (hex >= 'a' && hex <= 'f') return hex - 'a' + 10;
    else if (hex >= 'A' && hex <= 'F') return hex - 'A' + 10;
    else return 0;
}

uint8_t char2int(uint8_t x) {
    if (x >= '0' && x <= '9') return x - '0';
    else return 0;
}

/*@}*/

int main() {
    Init();
    sei();
    while(1){
        if (DataInReceiveBuffer()) {
            uint8_t temp = USART0_Receive();
            if (temp == '#') {
                    temp = USART0_Receive();
                    switch(temp) {
                        case 'S':
                            temp = char2int(USART0_Receive());
                            uint8_t buf[9];
                            for (uint8_t i=0; i<9; i++) {
                                buf[i] = hex2int(USART0_Receive());
                            }
                            leds[RED][temp]   = (buf[0] << 8 | buf[1] << 4 | buf[2]) & 0x1FF;
                            leds[GREEN][temp] = (buf[3] << 8 | buf[4] << 4 | buf[5]) & 0x1FF;
                            leds[BLUE][temp]  = (buf[6] << 8 | buf[7] << 4 | buf[8]) & 0x1FF;
                            break;
                        case 'T':
                            USART0_Transmit('#');
                            USART0_Transmit('O');
                            USART0_Transmit('K');
                        default:
                            break;
                    }
            }
        }
    }
}

/*@{*/ // Interrupts section

ISR (TIMER0_OVF_vect) {
    TCNT0 = 200;
    if (countPWM++ == MAXPWM) {
        countPWM = 0;
        for (uint8_t i=0; i<COLORS; i++) {
            for (uint8_t j=0; j<CHANELS; j++) {
                leds_buff[i][j] = leds[i][j];
            }
        }
        // Common anode or common cathode
#if COMMON == CATHODE
    #if CHANELS > 0
        if (leds_buff[RED][0])     PORT_RED0   |= 1<<RED0;
        if (leds_buff[GREEN][0])   PORT_GREEN0 |= 1<<GREEN0;
        if (leds_buff[BLUE][0])    PORT_BLUE0  |= 1<<BLUE0;
    #endif
    #if CHANELS > 1
        if (leds_buff[RED][1])     PORT_RED1   |= 1<<RED1;
        if (leds_buff[GREEN][1])   PORT_GREEN1 |= 1<<GREEN1;
        if (leds_buff[BLUE][1])    PORT_BLUE1  |= 1<<BLUE1;
    #endif
    #if CHANELS > 2
        if (leds_buff[RED][2])     PORT_RED2   |= 1<<RED2;
        if (leds_buff[GREEN][2])   PORT_GREEN2 |= 1<<GREEN2;
        if (leds_buff[BLUE][2])    PORT_BLUE2  |= 1<<BLUE2;
    #endif
    #if CHANELS > 3
        if (leds_buff[RED][3])     PORT_RED3   |= 1<<RED3;
        if (leds_buff[GREEN][3])   PORT_GREEN3 |= 1<<GREEN3;
        if (leds_buff[BLUE][3])    PORT_BLUE3  |= 1<<BLUE3;
    #endif
    #if CHANELS > 4
        if (leds_buff[RED][4])     PORT_RED4   |= 1<<RED4;
        if (leds_buff[GREEN][4])   PORT_GREEN4 |= 1<<GREEN4;
        if (leds_buff[BLUE][4])    PORT_BLUE4  |= 1<<BLUE4;
    #endif
    #if CHANELS > 5
        if (leds_buff[RED][5])     PORT_RED5   |= 1<<RED5;
        if (leds_buff[GREEN][5])   PORT_GREEN5 |= 1<<GREEN5;
        if (leds_buff[BLUE][5])    PORT_BLUE5  |= 1<<BLUE5;
    #endif
#elif COMMON == ANODE
    #if CHANELS > 0
        if (leds_buff[RED][0])     PORT_RED0   &= ~(1<<RED0);
        if (leds_buff[GREEN][0])   PORT_GREEN0 &= ~(1<<GREEN0);
        if (leds_buff[BLUE][0])    PORT_BLUE0  &= ~(1<<BLUE0);
    #endif
    #if CHANELS > 1
        if (leds_buff[RED][1])     PORT_RED1   &= ~(1<<RED1);
        if (leds_buff[GREEN][1])   PORT_GREEN1 &= ~(1<<GREEN1);
        if (leds_buff[BLUE][1])    PORT_BLUE1  &= ~(1<<BLUE1);
    #endif
    #if CHANELS > 2
        if (leds_buff[RED][2])     PORT_RED2   &= ~(1<<RED2);
        if (leds_buff[GREEN][2])   PORT_GREEN2 &= ~(1<<GREEN2);
        if (leds_buff[BLUE][2])    PORT_BLUE2  &= ~(1<<BLUE2);
    #endif
    #if CHANELS > 3
        if (leds_buff[RED][3])     PORT_RED3   &= ~(1<<RED3);
        if (leds_buff[GREEN][3])   PORT_GREEN3 &= ~(1<<GREEN3);
        if (leds_buff[BLUE][3])    PORT_BLUE3  &= ~(1<<BLUE3);
    #endif
    #if CHANELS > 4
        if (leds_buff[RED][4])     PORT_RED4   &= ~(1<<RED4);
        if (leds_buff[GREEN][4])   PORT_GREEN4 &= ~(1<<GREEN4);
        if (leds_buff[BLUE][4])    PORT_BLUE4  &= ~(1<<BLUE4);
    #endif
    #if CHANELS > 5
        if (leds_buff[RED][5])     PORT_RED5   &= ~(1<<RED5);
        if (leds_buff[GREEN][5])   PORT_GREEN5 &= ~(1<<GREEN5);
        if (leds_buff[BLUE][5])    PORT_BLUE5  &= ~(1<<BLUE5);
    #endif
#endif
    }
    // Common anode or common cathode
#if COMMON == CATHODE
    #if CHANELS > 0
    if (leds_buff[RED][0]   == countPWM)    PORT_RED0   &= ~(1<<RED0);
    if (leds_buff[GREEN][0] == countPWM)    PORT_GREEN0 &= ~(1<<GREEN0);
    if (leds_buff[BLUE][0]  == countPWM)    PORT_BLUE0  &= ~(1<<BLUE0);
    #endif
    #if CHANELS > 1
    if (leds_buff[RED][1]   == countPWM)    PORT_RED1   &= ~(1<<RED1);
    if (leds_buff[GREEN][1] == countPWM)    PORT_GREEN1 &= ~(1<<GREEN1);
    if (leds_buff[BLUE][1]  == countPWM)    PORT_BLUE1  &= ~(1<<BLUE1);
    #endif
    #if CHANELS > 2
    if (leds_buff[RED][2]   == countPWM)    PORT_RED2   &= ~(1<<RED2);
    if (leds_buff[GREEN][2] == countPWM)    PORT_GREEN2 &= ~(1<<GREEN2);
    if (leds_buff[BLUE][2]  == countPWM)    PORT_BLUE2  &= ~(1<<BLUE2);
    #endif
    #if CHANELS > 3
    if (leds_buff[RED][3]   == countPWM)    PORT_RED3   &= ~(1<<RED3);
    if (leds_buff[GREEN][3] == countPWM)    PORT_GREEN3 &= ~(1<<GREEN3);
    if (leds_buff[BLUE][3]  == countPWM)    PORT_BLUE3  &= ~(1<<BLUE3);
    #endif
    #if CHANELS > 4
    if (leds_buff[RED][4]   == countPWM)    PORT_RED4   &= ~(1<<RED4);
    if (leds_buff[GREEN][4] == countPWM)    PORT_GREEN4 &= ~(1<<GREEN4);
    if (leds_buff[BLUE][4]  == countPWM)    PORT_BLUE4  &= ~(1<<BLUE4);
    #endif
    #if CHANELS > 5
    if (leds_buff[RED][5]   == countPWM)    PORT_RED5   &= ~(1<<RED5);
    if (leds_buff[GREEN][5] == countPWM)    PORT_GREEN5 &= ~(1<<GREEN5);
    if (leds_buff[BLUE][5]  == countPWM)    PORT_BLUE5  &= ~(1<<BLUE5);
    #endif
#elif COMMON == ANODE
    #if CHANELS > 1
    if (leds_buff[RED][0]   == countPWM)    PORT_RED0   |= 1<<RED0;
    if (leds_buff[GREEN][0] == countPWM)    PORT_GREEN0 |= 1<<GREEN0;
    if (leds_buff[BLUE][0]  == countPWM)    PORT_BLUE0  |= 1<<BLUE0;
    #endif
    #if CHANELS > 1
    if (leds_buff[RED][1]   == countPWM)    PORT_RED1   |= 1<<RED1;
    if (leds_buff[GREEN][1] == countPWM)    PORT_GREEN1 |= 1<<GREEN1;
    if (leds_buff[BLUE][1]  == countPWM)    PORT_BLUE1  |= 1<<BLUE1;
    #endif
    #if CHANELS > 2
    if (leds_buff[RED][2]   == countPWM)    PORT_RED2   |= 1<<RED2;
    if (leds_buff[GREEN][2] == countPWM)    PORT_GREEN2 |= 1<<GREEN2;
    if (leds_buff[BLUE][2]  == countPWM)    PORT_BLUE2  |= 1<<BLUE2;
    #endif
    #if CHANELS > 3
    if (leds_buff[RED][3]   == countPWM)    PORT_RED3   |= 1<<RED3;
    if (leds_buff[GREEN][3] == countPWM)    PORT_GREEN3 |= 1<<GREEN3;
    if (leds_buff[BLUE][3]  == countPWM)    PORT_BLUE3  |= 1<<BLUE3;
    #endif
    #if CHANELS > 4
    if (leds_buff[RED][4]   == countPWM)    PORT_RED4   |= 1<<RED4;
    if (leds_buff[GREEN][4] == countPWM)    PORT_GREEN4 |= 1<<GREEN4;
    if (leds_buff[BLUE][4]  == countPWM)    PORT_BLUE4  |= 1<<BLUE4;
    #endif
    #if CHANELS > 5
    if (leds_buff[RED][5]   == countPWM)    PORT_RED5   |= 1<<RED5;
    if (leds_buff[GREEN][5] == countPWM)    PORT_GREEN5 |= 1<<GREEN5;
    if (leds_buff[BLUE][5]  == countPWM)    PORT_BLUE5  |= 1<<BLUE5;
    #endif
#endif
}

ISR (USART_RX_vect) {
    uint8_t data;
    uint8_t tmphead;
    data = UDR0;
    tmphead = (USART_RxHead + 1) & USART_RX_BUFFER_MASK;            // Calculate buffer index
    USART_RxHead = tmphead;                                         // Store new index
    if (tmphead == USART_RxTail) {
        /* ERROR! Receive buffer overflow */                        // TODO: refactory
    }
    USART_RxBuf[tmphead] = data;                                    // Store received data in buffer
}

ISR (USART_UDRE_vect) {
    uint8_t tmptail;
    if (USART_TxHead != USART_TxTail) {                             // Check if all data is transmitted
        tmptail = (USART_TxTail + 1) & USART_TX_BUFFER_MASK;        // Calculate buffer index
        USART_TxTail = tmptail;                                     // Store new index
        UDR0 = USART_TxBuf[tmptail];                                // Start transmition
    }
    else
        UCSR0B &= ~(1<<UDRIE0);
}

/*@}*/
