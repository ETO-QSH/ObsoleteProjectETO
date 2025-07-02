#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

int main_7_1(void) {
    int in;
    scanf("%d", &in);
    printf("%d", (in % 10) * 100 + (in / 10 % 10) * 10 + (in / 100));
    return 0;
}

int main_7_2(void) {
    int temp, sum = 0;
    for (int i = 0; i < 4; i++) {
        scanf("%d", &temp);
        sum += temp;
    }
    printf("Sum = %d; Average = %.1f", sum, (float) sum / 4);
    return 0;
}

int main_7_3(void) {
    int y, m, d;
    scanf("%d-%d-%d", &m, &d, &y);
    printf("%04d-%02d-%02d", y, m, d);
    return 0;
}

int main_7_4(void) {
    int d;
    char c;
    float f1, f2;
    scanf("%f %d %c %f", &f1, &d, &c, &f2);
    printf("%c %d %.2f %.2f", c, d, f1, f2);
    return 0;
}

int main_7_5(void) {
    int now, dump;
    scanf("%d %d", &now, &dump);
    int min = now / 100 * 60 + now % 100 + dump;
    printf("%d%d", min / 60, min % 60);
    return 0;
}

int main_7_6(void) {
    float money, year, rate;
    scanf("%f %f %f", &money, &year, &rate);
    printf("interest = %.2f", money * pow(1 + rate, year) - money);
    return 0;
}

int main_7_7(void) {
    float r1, r2;
    scanf("%f %f", &r1, &r2);
    printf("%.2f", 1.0 / (1.0 / r1 + 1.0 / r2));
    return 0;
}

int main_7_8(void) {
    int a;
    scanf("%d", &a);
    float b = pow(1.01, a), c = pow(0.99, a);
    printf("%.2f %.2f  %.1f%%", b, c, b * 100 / c);
    return 0;
}

int main_7_9(void) {
    int d;
    scanf("%d", &d);
    printf("%d%d", d / 16, d % 16);
    return 0;
}

int main_7_10(void) {
    float x;
    scanf("%f", &x);
    printf("f(%.2f) = %.2f", x, x >= 0 ? sqrt(x) : pow(x + 1, 2) + 1 / x + 2 * x);
    return 0;
}

int main_7_11(void) {
    int day;
    scanf("%d", &day);
    printf("%s in day %d", day % 5 > 3 ? "Drying" : "Fishing", day);
    return 0;
}

int main_7_12(void) {
    int start, end;
    scanf("%d %d", &start, &end);
    int dump = (end / 100 - start / 100) * 60 + end % 100 - start % 100;
    printf("%02d:%02d", dump / 60, dump % 60);
    return 0;
}

int main_7_13(void) {
    int a, b;
    char c;
    scanf("%d %c %d", &a, &c, &b);
    if (c == '+') {
        printf("%d", a + b);
    } else if (c == '-') {
        printf("%d", a - b);
    } else if (c == '*') {
        printf("%d", a * b);
    } else if (c == '/') {
        printf("%d", a / b);
    } else if (c == '%') {
        printf("%d", a % b);
    } else {
        printf("ERROR");
    }
    return 0;
}

int main_7_14(void) {
    char a;
    scanf("%c", &a);
    if (a >= '0' && a <= '9') {
        printf("This is a digit.");
    } else if (a >= 'A' && a <= 'Z') {
        printf("This is a capital letter.");
    } else if (a >= 'a' && a <= 'z') {
        printf("This is a small letter.");
    } else {
        printf("Other character.");
    }
    return 0;
}


int main_7_15(void) {
    int y, m, d;
    int days[13] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 10086};
    scanf("%d-%d-%d", &y, &m, &d);
    if ((y % 4 == 0 && y % 100 != 0) || y % 400 == 0) {
        days[1] += 1;
    }
    int ans = days[m - 1] - d + 1;
    for (;m++ < 12;) {
        ans += days[m - 1];
    }
    printf("还有%d天到新年", ans);
    return 0;
}

int main_7_16(void) {
    int p, w, s;
    float a, ds[6] = {1.00, 0.98, 0.95, 0.92, 0.90, 0.85};
    scanf("%d %d %d", &p, &w, &s);
    if (s < 250) {
        a = ds[0];
    } else if (s < 500) {
        a = ds[1];
    } else if (s < 1000) {
        a = ds[2];
    } else if (s < 2000) {
        a = ds[3];
    } else if (s < 3000) {
        a = ds[4];
    } else {
        a = ds[5];
    }
    printf("freight=%.2f", p * w * s * a);
    return 0;
}

int main_7_17(void) {
    int a, b, c, d;
    scanf("%d %d %d %d", &c, &d, &a, &b);
    if (a < c && b < c) {
        printf("%d-N %d-N\nzhang da zai lai ba", a, b);
    }
    if (a > c && b > c) {
        printf("%d-Y %d-Y\nhuan ying ru guan", a, b);
    }
    if (a >= c && a < d && b < c) {
        printf("%d-Y %d-N\n1: huan ying ru guan", a, b);
    }
    if (b >= c && b < d && a < c) {
        printf("%d-N %d-Y\n2: huan ying ru guan", a, b);
    }
    if (a < c && b >= d) {
        printf("%d-Y %d-Y\nqing 2 zhao gu hao 1", a, b);
    }
    if (b < c && a >= d) {
        printf("%d-Y %d-Y\nqing 1 zhao gu hao 2", a, b);
    }
    return 0;
}

int main_7_18(void) {
    int fz = 1, fm = 1, N, b = 0;
    float ans = 0;
    scanf("%d", &N);
    for (; N--; fm += 2) {
        ans += (float) ((b++ % 2 == 1 ? -1 : 1) * fz++) / fm;
    }
    printf("%.3f", ans);
    return 0;
}

int main_7_19(void) {
    int index = 0, temp;
    do {
        scanf("%d", &temp);
        index++;
    } while (temp != 250);
    printf("%d", index);
    return 0;
}

int gcd(int a, int b) {
    int temp;
    while (b != 0) {
        temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

int main_7_20(void) {
    int a, b;
    scanf("%d %d", &a, &b);
    int g = gcd(a, b);
    printf("%d %d", g, a * b / g);
    return 0;
}

int main_7_21(void) {
    int letter = 0, blank = 0, digit = 0, other = 0;
    char ch;
    for (int i = 0; i < 10; i++) {
        ch = getchar();
        if (ch >= 'a' && ch <= 'z' || ch >= 'A' && ch <= 'Z') {
            letter++;
        } else if (ch == '\n' || ch == ' ') {
            blank++;
        } else if (ch >= '0' && ch <= '9') {
            digit++;
        } else {
            other++;
        }
    }
    printf("letter = %d, blank = %d, digit = %d, other = %d", letter, blank, digit, other);
    return 0;
}

int main_7_22() {
    int h, m;
    scanf("%d:%d", &h, &m);
    if (h < 12 || (h == 12 && m == 0)) {
        printf("Only %02d:%02d. Too early to Dang.\n", h, m);
    } else {
        for (int i = 0; i < h; i++) {
            printf("Dang ");
        }
        printf("\n");
    }
    return 0;
}

int main_7_23() {
    int temp, Tom = 0, Jerry = 0, Spike = 0, Invalid = 0;
    while (true) {
        scanf("%d", &temp);
        if (temp == -1) {
            break;
        } else if (temp == 1) {
            Tom++;
        } else if (temp == 2) {
            Jerry++;
        } else if (temp == 3) {
            Spike++;
        } else {
            Invalid++;
        }
    }
    printf("Tom = %d Jerry = %d Spike = %d Invalid = %d", Tom, Jerry, Spike, Invalid);
    if (Invalid > Tom && Invalid > Jerry && Invalid > Spike) {
        printf("\nElection invalid!");
    }
    return 0;
}

int main_7_24(void) {
    int N, M;
    double price;
    scanf("%d %d", &N, &M);
    for (int i = 0; i < N; i++) {
        scanf("%lf", &price);
        if (price < M) {
            printf("On Sale! %.1lf\n", price);
        }
    }
    return 0;
}

int main_7_25(void) {
    int N;
    char lst[7];           // 6位数字加一个空字符（字符串结束标志）
    scanf("%d", &N);
    while (N--) {
        scanf("%s", &lst);
        printf("%s", lst[0] + lst[1] + lst[2] == lst[3] + lst[4] + lst[5] ? "You are lucky!" : "Wish you good luck.");
    }
    return 0;
}

int main_7_26(void) {
    float N;
    char ch;
    scanf("%f %c", &N, &ch);
    for (int i = 0; i < N / 2; i++) {
        for (int j = 0; j < N; j++) {
            printf("%c", ch);
        }
        printf("\n");
    }
    return 0;
}

int main_7_27() {
    int a, b, c;
    scanf("%d", &a);
    for (b = 1; b <= a; b++) {
        for (c = 1; c <= b; c++) {
            printf("%d*%d=%-4d", c, b, c * b);
        }
        printf("\n");
    }
    return 0;
}

int main_7_28(void) {
    int a, count = 0;
    scanf("%d", &a);
    for (int i = a; i < a + 4; i++) {
        for (int j = a; j < a + 4; j++) {
            for (int k = a; k < a + 4; k++) {
                if (i != j && i != k && j != k) {
                    printf("%d%c", i * 100 + j * 10 + k, ++count % 6 == 0 ? '\n' : ' ');
                }
            }
        }
    }
    return 0;
}

int main_7_29(void) {
    int N;
    bool t = false;
    scanf("%d", &N);
    for (int x = 1; x < 71; x++) {
        for (int y = 1; y < 71; y++) {
            if (x * x + y * y == N && x < y) {
                printf("%d %d\n", x, y);
                t = 1;
            }
        }
    }
    if (!t) {
        printf("No Solution");
    }
    return 0;
}

int main_7_30(void) {
    int N, temp, now;
    scanf("%d", &N);
    while (N--) {
        bool t = true;
        int flag = -1;
        scanf("%d", &temp);
        for (int i = 1; i < 10; i++) {
            now = temp * i;
            int sum = 0;
            while (now > 0) {
                sum += now % 10;
                now /= 10;
            }
            if (flag != -1) {
                if (flag != sum) {
                    t = false;
                }
            } else {
                flag = sum;
            }
        }
        if (t) {
            printf("%d\n", flag);
        } else {
            printf("NO\n");
        }
    }
    return 0;
}

int main_7_31(void) {
    int N, num = 0;
    char a, b;
    scanf("%d", &N);
    while (N--) {
        for (int i = 0; i < 4; i++) {
            scanf(" %c-%c", &a, &b);
            if (b == 'T') {
                num = a - 'A' + 1;
            }
        }
        printf("%d", num);
    }
    return 0;
}

int main_7_32(void) {
    int N;
    scanf("%d", &N);
    int start = pow(10, N - 1);
    int end = pow(10, N) - 1;
    for (int num = start; num <= end; num++) {
        int temp = num, sum = 0;
        while (temp > 0) {
            int digit = temp % 10;
            sum += pow(digit, N);
            temp /= 10;
        }
        if (sum == num) {
            printf("%d\n", num);
        }
    }
    return 0;
}

bool is_prime(int n) {
    if (n == 2 || n == 3) {
        return true;
    }
    for (int i = 2; i <= (int) sqrt(n); i++) {
        if (n % i == 0) {
            return false;
        }
    }
    return true;
}

int main_7_33(void) {
    int x, k, count = 0;
    scanf("%d %d", &x, &k);
    while (k) {
        if (is_prime(++x)) {
            printf("%d%c", x, ++count % 5 == 0 ? '\n' : ' ');
            k--;
        }
    }
    return 0;
}

int main_7_34(void) {
    int N, X, t;
    bool flag = false;
    scanf("%d %d", &N, &X);
    for  (int i = 0; i < N; i++) {
        scanf("%d", &t);
        if (t == X) {
            printf("%d", i);
            flag = true;
        }
    }
    if (!flag) {
        printf("\nNot Found");
    }
    return 0;
}

int main_7_35(void) {
    int N;
    scanf("%d", &N);
    int arr[N];
    for (int i = 0; i < N; i++) {
        scanf("%d", &arr[i]);
    }
    int min_index = 0;
    for (int i = 1; i < N; i++) {
        if (arr[i] < arr[min_index]) {
            min_index = i;
        }
    }
    int temp = arr[0];
    arr[0] = arr[min_index];
    arr[min_index] = temp;
    int max_index = N - 1;
    for (int i = 0; i < N; i++) {
        if (arr[i] > arr[max_index]) {
            max_index = i;
        }
    }
    temp = arr[N - 1];
    arr[N - 1] = arr[max_index];
    arr[max_index] = temp;
    for (int i = 0; i < N; i++) {
        printf("%d" , arr[i]);
    }
    return 0;
}

int main_7_36(void) {
    int N, X;
    scanf("%d", &N);
    int arr[N + 1];
    for (int i = 0; i < N; i++) {
        scanf("%d", &arr[i]);
    }
    scanf("%d", &X);
    for (int i = 0; i < N; i++) {
        if (arr[i] > X) {
            for (int n = N; i < n + 1; n--) {
                arr[n + 1] = arr[n];
            }
            arr[i] = X;
            break;
        }
    }
    for (int i = 0; i < N + 1; i++) {
        printf("%d " , arr[i]);
    }
    return 0;
}

int main_7_37(void) {
    int N, X, index = 0;
    bool flag, none = true;
    scanf("%d", &N);
    int arr[N];
    for (int i = 0; i < N; i++) {
        scanf("%d", &arr[i]);
    }
    scanf("%d", &X);
    do {
        flag = false;
        for (int i = index; i < N; i++) {
            if (arr[i] == X && !flag) {
                arr[i] = -4096;
                flag = true;
            } else if (flag) {
                index = i;
                break;
            }
        }
        if (flag || none) {
            for (int i = 0; i < N; i++) {
                if (arr[i] != -4096) {
                    printf("%d ", arr[i]);
                }
            }
            none = false;
            printf("\n");
        }
    } while (flag);
    return 0;
}

int main_7_38(void) {
    int m, n;
    scanf("%d %d", &n, &m);
    int temp[n];
    for (int t = 0; t < n; t++) {
        scanf("%d", &temp[t]);
    }
    for (int t = n; t < 2 * n; t++) {
        printf("%d ", temp[(t - m % n) % n]);
    }
    printf("\n");
    return 0;
}

int main_7_39(void) {
    int n, sum = 0;
    scanf("%d", &n);
    int matrix[n][n];
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            scanf("%d", &matrix[i][j]);
            if (i != n - 1 && j != n - 1 && i + j != n - 1) {
                sum += matrix[i][j];
            }
        }
    }
    printf("%d", sum);
    return 0;
}

int main_7_40(void) {
    int M, N;
    scanf("%d %d", &M, &N);
    int matrix[20][20];
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            scanf("%d", &matrix[i][j]);
        }
    }
    int found = 0;
    for (int i = 1; i < M - 1; i++) {
        for (int j = 1; j < N - 1; j++) {
            if (matrix[i][j] > matrix[i-1][j] && matrix[i][j] > matrix[i+1][j] &&
                matrix[i][j] > matrix[i][j-1] && matrix[i][j] > matrix[i][j+1]) {
                printf("%d %d %d\n", matrix[i][j], i+1, j+1);
                found = 1;
                }
        }
    }
    if (!found) {
        printf("None %d %d\n", M, N);
    }
    return 0;
}

int compare_str(const void *a, const void *b) {
    return strcmp(a, b);
}

int main_7_41(void) {
    char str[5][80];
    for (int i = 0; i < 5; i++) {
        scanf("%s", str[i]);
    }
    qsort(str, 5, sizeof(str[0]), compare_str);
    printf("After sorted:\n");
    for (int i = 0; i < 5; i++) {
        printf("%s\n", str[i]);
    }
    return 0;
}

int main_7_42(void) {
    int lst[10], min = 9;
    for (int i = 0; i < 10; i++) {
        scanf("%d", &lst[i]);
        if (i != 0 && i < min) {
            min = i;
        }
    }
    printf("%d", min);
    lst[min]--;
    for (int i = 0; i < 10; i++) {
        while (lst[i]--) {
            printf("%d", i);
        }
    }
    return 0;
}

int main_7_43(void) {
    int count = 0;
    bool flag = 0;
    char ch;
    while ((ch = getchar()) != '\n') {
        if (ch == ' ' && flag) {
            flag = 0;
        } else if (ch != ' ' && !flag) {
            flag = 1;
            count++;
        }
    }
    printf("%d", count);
    return 0;
}

int main_7_44(void) {
    int N;
    scanf("%d", &N);
    for (int i = 0; i < N; i++) {
        char str[81];
        scanf(" %[^\n]", str);
        if (str[strlen(str) - 1] == '?') {
            if (strstr(str, "PTA") != NULL) {
                printf("Yes!\n");
            } else {
                printf("No.\n");
            }
        } else {
            printf("enen\n");
        }
    }
    return 0;
}
