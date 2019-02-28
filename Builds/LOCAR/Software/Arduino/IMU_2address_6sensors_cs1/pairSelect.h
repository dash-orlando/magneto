/*
 * Switches between all the available sensors using the multiplexer
 */

// =======================    Select IMU pair       ====================
void pairSelect(int desiredPair) {
  int pair = desiredPair;
  if (pair == 1) {
    //s.t. the selection lines hit Y0, at 000
    digitalWrite(S0, LOW);
    digitalWrite(S1, LOW);
    delay(DEBOUNCE);
  } else if (pair == 2) {
    //s.t. the selection lines hit Y1, at 001
    digitalWrite(S0, HIGH);
    digitalWrite(S1, LOW);
    delay(DEBOUNCE);
  } else if (pair == 3) {
    //s.t. the selection lines hit Y1, at 010
    digitalWrite(S0, LOW);
    digitalWrite(S1, HIGH);
    delay(DEBOUNCE);
  } else {
    Serial.println( F("Error. This sensor pair doesn't exist!") );
    while (1);
  }
};
