/*
  Buddy Mini — V0.5 firmware starter (XIAO ESP32-C3 + ST7789 240x240 SPI)
  First wired milestone: greeting, cat, menu, quotes, family notes, Star Catch.
  No battery, motor, buzzer or touch sensor required for this milestone.

  INSTALL LIBRARIES (Arduino IDE Library Manager):
    Adafruit GFX Library
    Adafruit ST7735 and ST7789 Library

  Board: Seeed XIAO ESP32C3 / XIAO_ESP32C3 (ESP32 Arduino package)
  Wiring (ONLY after confirming LCD module is 3.3V compatible):
  LCD GND -> GND       LCD VCC -> 3V3 (subject to module spec)
  LCD SCL -> D8 (SPI SCK)
  LCD SDA -> D10 (SPI MOSI)
  LCD CS  -> D3
  LCD DC  -> D2
  LCD RST -> D4
  LCD BL  -> 3V3 (only if allowed by module specification)
  Left button: D1 to GND; Center button: D5 to GND; Right button: D7 to GND

  Caution: D8 (GPIO8) is a boot-strapping pin. Do not force it LOW during boot.
  D9 (BOOT button/GPIO9) and D0 (GPIO2) intentionally left unused.
*/

#include <Arduino.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>

constexpr int TFT_CS = D3;
constexpr int TFT_DC = D2;
constexpr int TFT_RST = D4;
constexpr int BUTTON_LEFT = D1;
constexpr int BUTTON_MIDDLE = D5;
constexpr int BUTTON_RIGHT = D7;

Adafruit_ST7789 tft(TFT_CS, TFT_DC, TFT_RST);

constexpr uint16_t BACK = 0xF6DB;       // soft pink
constexpr uint16_t DARK = 0x59AA;       // warm deep mauve
constexpr uint16_t PINK = 0xF24F;
constexpr uint16_t LIGHT = 0xFF1B;
constexpr uint16_t WHITE = 0xFFFF;
constexpr uint16_t GOLD = 0xFE40;

enum class Page : uint8_t { HOME, MENU, QUOTES, FAMILY, STARS };
Page page = Page::HOME;
int menuIndex = 0;
int quoteIndex = 0;
int familyIndex = 0;
int starLane = 1;
int score = 0;
int petHearts = 0;
unsigned long lastInteractionAt = 0;
unsigned long centerDownAt = 0;
bool centerHolding = false;
bool buttonHeld[3] = {false, false, false};
unsigned long lastPressAt[3] = {0,0,0};

const char *const MENU_ITEMS[] = { "Star Catch", "Kind Words", "Family Notes" };
const char *const QUOTES[] = {
  "Go Buddy Go!",
  "You are brave and strong!",
  "Your ideas matter!",
  "You can do hard things!",
  "Shine bright at cheer!"
};
const char *const FAMILY[] = {
  "You are appreciated!",
  "You make us so proud!",
  "Keep being your sweet self!"
};
constexpr int MENU_COUNT = sizeof(MENU_ITEMS) / sizeof(MENU_ITEMS[0]);
constexpr int QUOTE_COUNT = sizeof(QUOTES) / sizeof(QUOTES[0]);
constexpr int FAMILY_COUNT = sizeof(FAMILY) / sizeof(FAMILY[0]);

void centerText(const String &s, int y, uint8_t scale, uint16_t color) {
  tft.setTextSize(scale);
  tft.setTextColor(color);
  int16_t x1, y1;
  uint16_t w, h;
  tft.getTextBounds(s, 0, 0, &x1, &y1, &w, &h);
  int16_t x = max(0, (240 - (int)w) / 2);
  tft.setCursor(x, y);
  tft.print(s);
}

void header(const String &name) {
  tft.fillScreen(BACK);
  tft.fillRoundRect(8, 7, 224, 37, 12, PINK);
  centerText(name, 19, 2, WHITE);
}

void footer(const String &label) {
  tft.fillRoundRect(8, 206, 224, 27, 9, LIGHT);
  centerText(label, 214, 1, DARK);
}

void drawBow(int x, int y) {
  tft.fillTriangle(x, y + 8, x + 24, y, x + 24, y + 19, PINK);
  tft.fillTriangle(x + 47, y + 8, x + 24, y, x + 24, y + 19, PINK);
  tft.fillCircle(x + 24, y + 9, 9, GOLD);
}

void drawCat(bool blink = false) {
  // Simple original kawaii cat face; no external graphics required.
  tft.fillTriangle(42, 112, 47, 70, 98, 91, WHITE);
  tft.fillTriangle(198, 112, 193, 70, 142, 91, WHITE);
  tft.fillTriangle(56, 100, 58, 84, 79, 98, PINK);
  tft.fillTriangle(184, 100, 182, 84, 161, 98, PINK);
  tft.fillRoundRect(38, 92, 164, 94, 40, WHITE);
  drawBow(136, 77);
  tft.fillCircle(79, 151, 12, LIGHT);
  tft.fillCircle(161, 151, 12, LIGHT);
  if (blink) {
    tft.drawFastHLine(83, 132, 15, DARK);
    tft.drawFastHLine(143, 132, 15, DARK);
  } else {
    tft.fillRoundRect(87, 124, 9, 21, 4, DARK);
    tft.fillRoundRect(145, 124, 9, 21, 4, DARK);
  }
  tft.fillTriangle(115, 150, 125, 150, 120, 158, PINK);
  tft.drawLine(120, 157, 120, 164, DARK);
  tft.drawLine(120, 164, 111, 170, DARK);
  tft.drawLine(120, 164, 129, 170, DARK);
}

void drawHome() {
  header("HI BUDDY!");
  centerText("Your Cheer Cat", 52, 1, DARK);
  drawCat();
  centerText("Hearts: " + String(petHearts), 186, 1, DARK);
  footer("L: PET   M: MENU   R: MENU");
}

void drawMenu() {
  header("BUDDY'S MENU");
  centerText("Choose an adventure", 56, 1, DARK);
  for (int i = 0; i < MENU_COUNT; ++i) {
    int y = 82 + i * 38;
    const bool selected = i == menuIndex;
    tft.fillRoundRect(18, y, 204, 32, 10, selected ? PINK : LIGHT);
    centerText(String(selected ? "> " : "") + MENU_ITEMS[i] + (selected ? " <" : ""), y + 10, 1, selected ? WHITE : DARK);
  }
  footer("L/R: MOVE   M: SELECT");
}

void drawQuote() {
  header("KIND WORDS");
  centerText("A note for Buddy", 62, 2, DARK);
  tft.fillRoundRect(14, 105, 212, 80, 16, LIGHT);
  centerText(QUOTES[quoteIndex], 137, 1, DARK);
  footer("L/R: NEXT   M: MENU");
}

void drawFamily() {
  header("FAMILY NOTES");
  centerText("Good vibes for today", 64, 2, DARK);
  tft.fillRoundRect(14, 106, 212, 79, 16, LIGHT);
  centerText(FAMILY[familyIndex], 139, 1, DARK);
  footer("L/R: NEXT   M: MENU");
}

void drawStar(int lane, int y) {
  int x = 52 + lane * 68;
  tft.fillCircle(x, y, 14, GOLD);
  tft.fillCircle(x - 5, y - 3, 2, WHITE);
}

void drawStars() {
  header("STAR CATCH");
  centerText("Stars: " + String(score), 57, 2, DARK);
  for (int i = 0; i < 3; ++i) {
    int x = 15 + 70 * i;
    tft.drawRoundRect(x, 93, 69, 92, 10, PINK);
  }
  drawStar(starLane, 127);
  footer("LEFT     MIDDLE      RIGHT");
}

void drawCurrent() {
  switch(page) {
    case Page::HOME: drawHome(); break;
    case Page::MENU: drawMenu(); break;
    case Page::QUOTES: drawQuote(); break;
    case Page::FAMILY: drawFamily(); break;
    case Page::STARS: drawStars(); break;
  }
}

void nextStar(int chosenLane) {
  if (chosenLane == starLane) ++score;
  starLane = random(0, 3);
  drawStars();
}

void onButton(int which) {
  lastInteractionAt = millis();
  if (page == Page::HOME) {
    if (which == 0) {
      ++petHearts;
      drawHome();
    } else {
      page = Page::MENU;
      drawMenu();
    }
    return;
  }
  if (page == Page::MENU) {
    if (which == 0) menuIndex = (menuIndex + MENU_COUNT - 1) % MENU_COUNT;
    if (which == 2) menuIndex = (menuIndex + 1) % MENU_COUNT;
    if (which == 1) {
      page = menuIndex == 0 ? Page::STARS : (menuIndex == 1 ? Page::QUOTES : Page::FAMILY);
    }
    drawCurrent();
    return;
  }
  if (page == Page::STARS) {
    nextStar(which);
    return;
  }
  if (page == Page::QUOTES) {
    if (which == 1) page = Page::MENU;
    else quoteIndex = (quoteIndex + (which == 0 ? QUOTE_COUNT - 1 : 1)) % QUOTE_COUNT;
    drawCurrent();
    return;
  }
  if (page == Page::FAMILY) {
    if (which == 1) page = Page::MENU;
    else familyIndex = (familyIndex + (which == 0 ? FAMILY_COUNT - 1 : 1)) % FAMILY_COUNT;
    drawCurrent();
  }
}

void setup() {
  pinMode(BUTTON_LEFT, INPUT_PULLUP);
  pinMode(BUTTON_MIDDLE, INPUT_PULLUP);
  pinMode(BUTTON_RIGHT, INPUT_PULLUP);
  randomSeed((uint32_t) micros());
  SPI.begin(D8, D9, D10, TFT_CS);
  tft.init(240, 240);
  tft.setRotation(0);
  tft.setTextWrap(false);
  drawHome();
}

void loop() {
  const int pin[3] = { BUTTON_LEFT, BUTTON_MIDDLE, BUTTON_RIGHT };
  unsigned long now = millis();
  for (int i = 0; i < 3; ++i) {
    bool pressed = digitalRead(pin[i]) == LOW;
    if (pressed && !buttonHeld[i] && now - lastPressAt[i] > 45) {
      buttonHeld[i] = true;
      lastPressAt[i] = now;
      if (i == 1) { centerDownAt = now; centerHolding = true; }
      onButton(i);
    } else if (!pressed && buttonHeld[i]) {
      buttonHeld[i] = false;
      if (i == 1) centerHolding = false;
    }
  }
  // Hold center for 1.1 seconds to go home from any screen.
  if (centerHolding && buttonHeld[1] && now - centerDownAt >= 1100) {
    centerHolding = false;
    page = Page::HOME;
    drawHome();
  }
  delay(8);
}
