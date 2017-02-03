void setup() {
    Serial.begin(9600);
}

void loop() {
    if (Serial.available() > 0) {
        int incomingByte = Serial.read();
        if (incomingByte == '#') {
            int flag = 0;
            char msg[3];
            while (flag<3) {
                if (Serial.available() > 0) {
                    msg[flag++] = Serial.read();
                }
            }
            for (int i=0; i<sizeof(msg); i++)
                Serial.println(msg[i]);
        }
    }
}
