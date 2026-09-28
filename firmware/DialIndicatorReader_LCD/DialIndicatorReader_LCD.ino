/*
  DialIndicatorReader_LCD - same reader as DialIndicatorReader.ino, with a
  16x2 LCD showing the live reading plus the min/max seen so far, and an
  optional push button that sets a relative zero and clears min/max.

  Line 1:  10.01 mm
  Line 2:  L:9.98  H:10.05

  Author: Md. Mahin Rahman
  GitHub: https://github.com/thisisdibbo
  Email : mr.d2003feb@gmail.com

  MIT License - see LICENSE.
*/

// ---------------------------------------------------------------- config --

#define CLK_PIN    2
#define DATA_PIN   3
#define ZERO_PIN   4      // push button to GND, internal pull-up (optional)

#define SIGNAL_INVERTED true
#define RESOLUTION 100    // 100 = 0.01 mm tools, 1000 = 0.001 mm
#define BAUD 115200

#define USE_I2C_LCD 1     // 1 = I2C backpack, 0 = 6-wire parallel HD44780
#define LCD_I2C_ADDR 0x27

#define IDLE_GAP_US     2000UL
#define BIT_TIMEOUT_US 20000UL

#define DATA_BITS 24
#define SIGN_BIT  20
#define INCH_BIT  23

#if USE_I2C_LCD
  #include <Wire.h>
  #include <LiquidCrystal_I2C.h>
  LiquidCrystal_I2C lcd(LCD_I2C_ADDR, 16, 2);
#else
  #include <LiquidCrystal.h>
  // RS, E, D4, D5, D6, D7  (D2/D3 are taken by the caliper lines)
  LiquidCrystal lcd(12, 11, 10, 9, 8, 7);
#endif

long zeroOffset = 0;
long minValue = 0, maxValue = 0;
bool haveRange = false;

// ------------------------------------------------------------- reading ----

static inline bool readLine(uint8_t pin) {
  bool v = digitalRead(pin);
  return SIGNAL_INVERTED ? !v : v;
}

void waitForPacketGap() {
  unsigned long quietSince = micros();
  while (micros() - quietSince < IDLE_GAP_US) {
    if (!readLine(CLK_PIN)) quietSince = micros();
  }
}

bool readBit(bool &ok) {
  unsigned long t = micros();
  while (readLine(CLK_PIN)) {
    if (micros() - t > BIT_TIMEOUT_US) { ok = false; return false; }
  }
  t = micros();
  while (!readLine(CLK_PIN)) {
    if (micros() - t > BIT_TIMEOUT_US) { ok = false; return false; }
  }
  return readLine(DATA_PIN);
}

long readPacket(bool &ok) {
  long out = 0;
  for (uint8_t i = 0; i < DATA_BITS; i++) {
    bool bit = readBit(ok);
    if (!ok) return 0;
    out |= bit ? 1L << DATA_BITS : 0L;
    out >>= 1;
  }
  return out;
}

long decode(long raw, bool &inch) {
  inch = raw & (1L << INCH_BIT);
  bool negative = raw & (1L << SIGN_BIT);
  long value = raw & ((1L << SIGN_BIT) - 1L);
  return negative ? -value : value;
}

// ------------------------------------------------------------ formatting --

void formatValue(long value, bool inch, char *buf, bool withUnit) {
  double v;
  uint8_t decimals;
  const char *unit;
#if RESOLUTION == 100
  if (inch) { v = value / 2000.0;  decimals = 4; unit = " in"; }
  else      { v = value / 100.0;   decimals = 2; unit = " mm"; }
#else
  if (inch) { v = value / 20000.0; decimals = 5; unit = " in"; }
  else      { v = value / 1000.0;  decimals = 3; unit = " mm"; }
#endif
  dtostrf(v, 0, decimals, buf);
  if (withUnit) strcat(buf, unit);
}

void showOnLcd(long value, bool inch) {
  char line[17], num[16], lo[16], hi[16];

  formatValue(value, inch, num, true);
  snprintf(line, sizeof(line), "%-16s", num);
  lcd.setCursor(0, 0);
  lcd.print(line);

  formatValue(minValue, inch, lo, false);
  formatValue(maxValue, inch, hi, false);
  // %-6.6s caps each field at 6 characters so the line stays within 16 columns
  snprintf(line, sizeof(line), "L%-6.6s H%-6.6s", lo, hi);
  lcd.setCursor(0, 1);
  lcd.print(line);
}

// Press the button to make the current reading the new zero and clear min/max.
void checkZeroButton(long absolute) {
  static unsigned long lastChange = 0;
  static bool lastState = HIGH;
  bool state = digitalRead(ZERO_PIN);
  if (state != lastState && millis() - lastChange > 50) {
    lastChange = millis();
    lastState = state;
    if (state == LOW) {
      zeroOffset = absolute;
      haveRange = false;
      lcd.clear();
    }
  }
}

// ------------------------------------------------------- setup and loop ---

void setup() {
  pinMode(CLK_PIN, INPUT);
  pinMode(DATA_PIN, INPUT);
  pinMode(ZERO_PIN, INPUT_PULLUP);

  Serial.begin(BAUD);

#if USE_I2C_LCD
  lcd.init();
  lcd.backlight();
#else
  lcd.begin(16, 2);
#endif
  lcd.setCursor(0, 0);
  lcd.print("DialIndicator");
  lcd.setCursor(0, 1);
  lcd.print("waiting...");
}

void loop() {
  waitForPacketGap();

  bool ok = true;
  long raw = readPacket(ok);
  if (!ok) return;

  bool inch;
  long absolute = decode(raw, inch);

  checkZeroButton(absolute);
  long value = absolute - zeroOffset;

  if (!haveRange) {
    minValue = maxValue = value;
    haveRange = true;
  } else {
    if (value < minValue) minValue = value;
    if (value > maxValue) maxValue = value;
  }

  showOnLcd(value, inch);

  char buf[16];
  formatValue(value, inch, buf, true);
  Serial.println(buf);
}
