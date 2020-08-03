double f(double x) {
    return x + 1.0;
}

int power(int i) {
    int x;
    x = -5;
    x = i - 8;
    if (i > 0)
        power(i - 1);
    else {
        Print(f(3.14));
        return 8;
    }
    Print("1: ", i, ", 2: ", x);
    i = 800 + i;
    return i * 2;
}

int main() {
    power(5);
    return 68;
}