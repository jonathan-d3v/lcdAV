#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

byte d[8][8] = {
  {0,0,0,0,0,0,0,31}, {0,0,0,0,0,0,31,31}, {0,0,0,0,0,31,31,31}, 
  {0,0,0,0,31,31,31,31}, {0,0,0,31,31,31,31,31}, {0,0,31,31,31,31,31,31}, 
  {0,31,31,31,31,31,31,31}, {31,31,31,31,31,31,31,31}
};

void setup() {
  lcd.init();
  lcd.backlight();
  Serial.begin(115200);
  
  for(int i=0; i<8; i++) {
    lcd.createChar(i, d[i]);
  }
  
  lcd.clear();
  lcd.print("SYNCING...");
}

void loop() {
  if (Serial.available() > 0) {
    if (Serial.read() == 'S') { 
      // Time-out protection: if data is partial, don't hang
      long startTime = millis();
      while (Serial.available() < 16) {
        if (millis() - startTime > 50) return; // Drop frame if too slow
      }

      for (int i = 0; i < 16; i++) {
        int level = Serial.read();
        if (level > 8) level = 8;

        // TOP ROW (Grow Down)
        lcd.setCursor(i, 0);
        if (level >= 1) lcd.write(byte(level - 1));
        else lcd.print(" ");

        // BOTTOM ROW (Mirror)
        lcd.setCursor(i, 1);
        if (level >= 1) lcd.write(byte(level - 1));
        else lcd.print(" ");
      }
    }
  }
}