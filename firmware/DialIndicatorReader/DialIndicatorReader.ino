/*
  DialIndicatorReader - read a cheap Chinese digital caliper / dial indicator
  with an Arduino Nano and stream the measurement over USB serial.

  The instrument's 4-pin port runs at ~1.5 V logic, so CLK and DATA are
  level-shifted to 5 V with two NPN transistors in common-emitter stages.
  That stage inverts both signals, which is undone by SIGNAL_INVERTED below.
  Wiring and the transistor circuit: docs/hardware.md
  Packet format: docs/protocol.md

  Author: Md. Mahin Rahman
  GitHub: https://github.com/thisisdibbo
  Email : mr.d2003feb@gmail.com

  MIT License - see LICENSE.
*/

// ---------------------------------------------------------------- config --

#define CLK_PIN    2      // caliper CLOCK via level shifter
#define DATA_PIN   3      // caliper DATA  via level shifter
#define LED_PIN   13      // blinks once per packet (comment out to disable)

// The NPN common-emitter level shifter inverts the signals.
// Set to false only if you feed the pins with a non-inverting shifter.
#define SIGNAL_INVERTED true

// Instrument resolution: 100 for 0.01 mm tools (most calipers),
//                       1000 for 0.001 mm dial indicators.
#define RESOLUTION 100

#define PRINT_UNITS true  // false -> bare numbers, e.g. "10.01"
#define BAUD 115200

// Timing. Bits inside a packet are a few hundred us apart, packets are
// ~100-300 ms apart, so a quiet clock means we are between packets.
#define IDLE_GAP_US     2000UL
#define BIT_TIMEOUT_US 20000UL

// -------------------------------------------------------------- protocol --

#define DATA_BITS 24
#define SIGN_BIT  20
#define INCH_BIT  23

// ------------------------------------------------------------- reading ----

// Read a pin as the instrument drives it, undoing the inverting shifter.
static inline bool readLine(uint8_t pin) {
  bool v = digitalRead(pin);
  return SIGNAL_INVERTED ? !v : v;
}

// Block until the clock has been idle (high) long enough to be sure we are
// sitting in the gap between two packets, so bit 0 is really bit 0.
void waitForPacketGap() {
  unsigned long quietSince = micros();
  while (micros() - quietSince < IDLE_GAP_US) {
    if (!readLine(CLK_PIN)) quietSince = micros();   // burst still running
  }
}

// One bit: wait for the falling edge, then the rising edge, sample DATA.
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

// 24 bits, LSB first.
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

// Split the packet into a signed count and the unit flag.
long decode(long raw, bool &inch) {
  inch = raw & (1L << INCH_BIT);
  bool negative = raw & (1L << SIGN_BIT);
  long value = raw & ((1L << SIGN_BIT) - 1L);
  return negative ? -value : value;
}

// ------------------------------------------------------------- printing ---

void printValue(long value, bool inch) {
  double v = value;
#if RESOLUTION == 100
  if (inch) { Serial.print(v / 2000.0, 4);  if (PRINT_UNITS) Serial.print(" in"); }
  else      { Serial.print(v / 100.0,  2);  if (PRINT_UNITS) Serial.print(" mm"); }
#else
  if (inch) { Serial.print(v / 20000.0, 5); if (PRINT_UNITS) Serial.print(" in"); }
  else      { Serial.print(v / 1000.0,  3); if (PRINT_UNITS) Serial.print(" mm"); }
#endif
}

void blink() {
#ifdef LED_PIN
  static bool state = false;
  state = !state;
  digitalWrite(LED_PIN, state);
#endif
}

// ------------------------------------------------------- setup and loop ---

void setup() {
  pinMode(CLK_PIN, INPUT);
  pinMode(DATA_PIN, INPUT);
#ifdef LED_PIN
  pinMode(LED_PIN, OUTPUT);
#endif
  Serial.begin(BAUD);
}

void loop() {
  waitForPacketGap();

  bool ok = true;
  long raw = readPacket(ok);
  if (!ok) return;            // packet cut short - resync and try again

  bool inch;
  long value = decode(raw, inch);

  printValue(value, inch);
  Serial.println();
  blink();
}
