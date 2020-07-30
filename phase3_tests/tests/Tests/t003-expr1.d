int main() {
    int a;
    int b;
    int c;
    int d;

    int z;

    z = a + (b * 5);
    a = z * d;
    z = 2 * a + ((a + b) / (c + d));
    b = z / a;
    c = b * a + z;
    d = a - b - c - d - z;

    Print(a);
    Print(b);
    Print(c);
    Print(d);

    Print(z);
}