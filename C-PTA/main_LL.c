#include <stdio.h>
#include <math.h>
#include <string.h>

int main_5_1(void) {
    printf("\n");
    printf("       *\n");
    printf("       *\n");
    printf("       *\n");
    printf("   *   *   *\n");
    printf("   *********\n");
    printf("   *   *   *\n");
    printf("   *   *   *\n");
    printf("   *   *   *\n");
    printf("   *********\n");
    printf("   *   *   *\n");
    printf("       *\n");
    printf("       *\n");
    printf("       *\n");
    printf("       *\n");
    return 0;
}

int main_5_2(void) {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d", a * b);
    return 0;
}

int main_5_3(void) {
    char str[3];
    scanf("%s", &str);
    printf("%d", (int)str[0] + (int)str[1] + (int)str[2] - 48 * 3);
    return 0;
}

int main_5_4(void) {
    int H;
    scanf("%d", &H);
    float W = (H - 100) * 0.9 * 2;
    printf("%.1f", W);
    return 0;
}

int main_5_5(void) {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d + %d = %d\n", a, b, a + b);
    printf("%d - %d = %d\n", a, b, a - b);
    printf("%d * %d = %d\n", a, b, a * b);
    printf("%d / %d = %d\n", a, b, a / b);
    return 0;
}

int main_5_6(void) {
    int t;
    scanf("%d", &t);
    printf("height = %.2f", t * t * 9.8 / 2);
    return 0;
}

int main_5_7(void) {
    int x, y;
    scanf("%d %d", &x, &y);
    printf("%d", 100 * (x - y) / 2);
    return 0;
}

int main_5_8(void) {
    int num;
    scanf("%d", &num);
    printf("%d", (num + 2) / 3);
    return 0;
}

int main_5_9(void) {
    int foot, inch, cm;
    scanf("%d", &cm);
    foot = cm / 30.48;
    inch = ((float) cm / 30.48 - foot) * 12;
    printf("%d %d", foot, inch);
    return 0;
}

int main_5_10(void) {
    int A, B;
    scanf("%d %d", &A, &B);
    if (B == 0) {
        printf("%d/%d=Error", A, B);
    } else if (B < 0) {
        printf("%d/(%d)=%.2f", A, B, (float) A / B);
    } else {
        printf("%d/%d=%.2f", A, B, (float) A / B);
    }
    return 0;
}

int main_5_11(void) {
    float km;
    int min;
    scanf("%f %d", &km, &min);
    float cost = 10 + 2 * (min / 5);
    if (km > 3) {
        cost += 2 * (km - 3);
    }
    if (km > 10) {
        cost += km - 10;
    }
    printf("%d", (int) round(cost));
    return 0;
}

int main_5_12(void) {
    char c, a, b;
    scanf("%s", &c);
    if (c == 65 || c == 97) {
        a = c + 25; b = c + 1;
    } else if (c == 90 || c == 122) {
        a = c - 1; b = c - 25;
    } else {
        a = c - 1; b = c + 1;
    }
    printf("%c %d\n%c %d", a, a, b, b);
    return 0;
}

int main_5_13(void) {
    int day;
    scanf("%d", &day);
    if (day == 5) {
        printf("7");
    } else {
        printf("%d", (day + 2) % 7);
    }
    return 0;
}

int main_5_14(void) {
    float h, w, bmi;
    scanf("%f, %f", &h, &w);
    bmi = w / (h * h);
    printf("BMI = %.1f\n", bmi);
    if (bmi < 18.5) {
        printf("Under Weight");
    } else if (bmi < 24) {
        printf("Normal");
    } else if (bmi < 28) {
        printf("Over Weight");
    } else if (bmi < 32) {
        printf("Fat");
    } else {
        printf("Too Fat");
    }
    return 0;
}

int main_5_15(void) {
    int h, m;
    scanf("%d:%d", &h, &m);
    if (h < 12) {
        printf("%d:%d AM", h, m);
    } else {
        printf("%d:%d PM", h - 12, m);
    }
    return 0;
}

int main_5_16(void) {
    int y, m, d;
    int days[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    scanf("%d-%d-%d", &y, &m, &d);
    if ((y % 4 == 0 && y % 100 != 0) || y % 400 == 0) {
        days[1] += 1;
    }
    while (--m) {
        d += days[m];
    }
    printf("%d", d);
    return 0;
}

int main_5_17(void) {
    int v, u;
    scanf("%d %d", &v, &u);
    int f = round((float) (v - u) * 100 / u);
    if (f >= 10 && f < 50) {
        printf("Exceed %d%%. Ticket 200", f);
    } else if (f >= 50) {
        printf("Exceed %d%%. License Revoked", f);
    } else {
        printf("OK");
    }
    return 0;
}

int main_5_18(void) {
    int y, h, x;
    scanf("%d %d", &y, &h);
    if (y < 5) {
        x = 30;
    } else {
        x = 50;
    }
    float ans = h * x;
    if (h > 40) {
        ans += (h - 40) * x * 0.5;
    }
    printf("%.2f", ans);
    return 0;
}

int main_5_19(void) {
    int cost;
    scanf("%d", &cost);
    if (cost <= 3200) {
        printf("不需加班,可购买");
    } else if (cost <= 4800) {
        printf(" 需加班%d小时,可购买", (cost - 3200) / 40);
    } else {
        printf(" 需加班%d小时,买不起", (cost - 3200) / 40);
    }
    return 0;
}

int main_5_20(void) {
    int ans = 0;
    char ch;
    while ((ch = getchar()) != '\n') {
        if (ch != '-') {
            ans += 1;
        }
    }
    printf("%d", ans);
    return 0;
}

int main_5_21(void) {
    int num;
    double ans = 0;
    scanf("%d", &num);
    while (num--) {
        ans += sqrt(num + 1);
    }
    printf("sum = %.2f", ans);
    return 0;
}

int main_5_22(void) {
    int num;
    scanf("%d", &num);
    for (int i = 0; i <= num; i++) {
        printf("pow(3,%d) = %d\n", i, (int) pow(3, i));
    }
    return 0;
}

int main_5_23(void) {
    int num;
    bool r = 0;
    scanf("%d", &num);
    for (int y = 2001; y <= num; y++) {
        if ((y % 4 == 0 && y % 100 != 0) || y % 400 == 0) {
            printf("%d\n", y);
            r = true;
        }
    }
    if (!r) {
        printf("Invalid year!");
    }
    return 0;
}

int main_5_24(void) {
    int len;
    float num, sum = 0, min = 10, max = 0;
    scanf("%d", &len);
    for (int i = 0; i < len; i++) {
        scanf("%f", &num);
        sum += num;
        if (num < min) {
            min = num;
        }
        if (num > max) {
            max = num;
        }
    }
    printf("%.2f", (sum - min - max) / (len - 2));
    return 0;
}

int main_5_25(void) {
    int len, A = 0, B = 0, C = 0, D = 0, E = 0;
    float num;
    scanf("%d", &len);
    for (int i = 0; i < len; i++) {
        scanf("%f", &num);
        switch ((int) (num / 10) - 6) {
            case 4: case 3:
                A++; break;
            case 2:
                B++; break;
            case 1:
                C++; break;
            case 0:
                D++; break;
            default:
                E++;
        }
    }
    printf("%d %d %d %d %d", A, B, C, D, E);
    return 0;
}

int main_5_26(void) {
    int ch;
    while ((ch = getchar()) != '\n') {
        switch (ch) {
            case 67: case 99:
                printf("BEIJING OLYMPIC GAMES\n"); break;
            case 74: case 106:
                printf("JAPAN WORLD CUP\n"); break;
            case 75: case 107:
                printf("KOREA WORLD CUP\n"); break;
            default:
                printf("%c\n", ch);
        }
    }
    return 0;
}

int main_5_27(void) {
    int num;
    char type;
    float height;
    scanf("%d", &num);
    while (num--) {
        scanf(" %c %f", &type, &height);      // %c 前的空格用于跳过任何空白字符
        if (type == 'F') {                          // 单引号指代字符
            printf("%.2f\n", height * 1.09);
        } else {
            printf("%.2f\n", height / 1.09);
        }
    }
    return 0;
}

int main_5_28(void) {
    int fz_1 = 2, fm_1 = 1, fz_2 = 3, fm_2 = 2, fz_t, fm_t, len;
    double ans = (float) fz_1 / fm_1;
    scanf("%d", &len);
    while (--len) {
        ans += (float) fz_2 / fm_2;
        fz_t = fz_1; fm_t = fm_1;
        fz_1 = fz_2; fm_1 = fm_2;
        fz_2 += fz_t; fm_2 += fm_t;
    }
    printf("%.2f", ans);
    return 0;
}

int main_5_29(void) {
    int N, n = 1;
    scanf("%d", &N);
    while (--N) {
        n = (n + 1) * 2;
    }
    printf("%d", n);
    return 0;
}

int main_5_30(void) {
    int a, n, ans = 0;
    scanf("%d %d", &a, &n);
    for (int i = 0; i <= n; i++) {
        ans += a * i * pow(10, n - i);
    }
    printf("%d", ans);
    return 0;
}

int main_5_31(void) {
    int num, b = 0;
    scanf("%d", &num);
    for (int man = 0; man <= num / 3; man++) {
        for (int woman = 0; woman <= (num - man * 3) / 2; woman++) {
            int child = (num - man * 3 - woman * 2) * 2;
            if (man + woman + child == num) {
                printf("men=%d women=%d child=%d\n", man, woman, child);
                b = 1;
            }
        }
    }
    if (!b) {
        printf("No solution!");
    }
    return 0;
}

int main_5_32(void) {
    int N, count = 65;
    scanf("%d", &N);
    while (N--) {
        for (int n = N + 1; n--;) {
            printf("%c ", count++);
        }
        printf("\n");
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

int main_5_33(void) {
    int N, count = 0;
    scanf("%d", &N);
    for (int i = 2; i <= N; i++) {
        if (is_prime(i)) {
            if (++count % 8 == 0) {
                printf("%5d\n", i);
            } else {
                printf("%5d", i);
            }
        }
    }
    return 0;
}

int main_5_34(void) {
    int N;
    scanf("%d", &N);
    for (int n = 2; n <= N; n++) {
        if (is_prime(pow(2, n) - 1)) {
            printf("%d\n", (int) pow(2, n) - 1);
        }
    }
    return 0;
}

int main_5_35(void) {
    int len, sum = 0;
    scanf("%d", &len);
    int lst[len];
    for (int i = 0; i < len; i++) {
        scanf("%d", &lst[i]);
        sum += lst[i];
    }
    float average = (float) sum / len;
    printf("average=%.2f\n", average);
    for (int i = 0; i < len; i++) {
        if (lst[i] < average) {
            printf("%d ", lst[i]);
        }
    }
    return 0;
}

int main_5_36(void) {
    int n, s, lst[10], len = 10;
    for (int i = 0; i < len; i++) {
        scanf("%d", &lst[i]);
    }
    scanf("%d", &n);
    while (n--) {
        scanf("%d", &s);
        lst[s - 1] += 10;
    }
    for (int i = 0; i < len; i++) {
        printf("%d ", lst[i]);
    }
    return 0;
}

int main_5_37(void) {
    int N, sum = 0;
    scanf("%d", &N);
    int lst[N];
    for (int i = 0; i < N; i++) {
        scanf("%d", &lst[i]);
    }
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            if (i != j) {
                sum += lst[i] * 10 + lst[j];
            }
        }
    }
    printf("%d", sum);
    return 0;
}

int main_5_38(void) {
    int N, K, t;
    scanf("%d %d", &N, &K);
    int lst[N];
    for (int i = 0; i < N; i++) {
        scanf("%d", &lst[i]);
    }
    for (int n = 0; n < K; n++) {
        for (int a = 0; a < N - n - 1; a++) {
            if (lst[a] > lst[a + 1]) {
                t = lst[a];
                lst[a] = lst[a + 1];
                lst[a + 1] = t;
            }
        }
    }
    for (int i = 0; i < N; i++) {
        printf("%d ", lst[i]);
    }
    return 0;
}

int main_5_39(void) {
    int temp, max_1 = 0, max_2 = 0, len = 10;
    while (len--) {
        scanf("%d", &temp);
        if (temp > max_1) {
            max_2 = max_1;
            max_1 = temp;
        } else if (temp > max_2) {
            max_2 = temp;
        }
    }
    printf("%d", max_2);
    return 0;
}

int main_5_40(void) {
    int N, t, new, count = 0;
    scanf("%d", &N);
    scanf("%d", &t);
    for (int i = 1; i < N; i++) {
        scanf("%d", &new);
        if (++count % 3 == 0) {
            printf("%d\n", new - t);
        } else {
            printf("%d ", new - t);
        }
        t = new;
    }
    return 0;
}

int main_5_41(void) {
    int num, min = 4096, max = 0;
    for (int i = 0; i < 9; i++) {
        scanf("%d", &num);
        if (num < min) {
            min = num;
        }
        if (num > max) {
            max = num;
        }
    }
    printf("max=%d min=%d", max, min);
    return 0;
}

int main_5_42(void) {
    int num, loc[4] = {0};
    for (int i = 0; i < 16; i++) {
        scanf("%d", &num);
        if (num < 60) {
            loc[i % 4] += 1;
        }
    }
    for (int i = 0; i < 4; i++) {
        printf("%d ", loc[i]);
    }
    return 0;
}

int main_5_43(void) {
    int num, size, temp;
    scanf("%d", &num);
    while (num--) {
        bool flag = true;
        scanf("%d", &size);
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                scanf("%d", &temp);
                if (i > j && temp != 0) {
                    flag = false;
                }
            }
        }
        printf("%s\n", flag ? "YES": "NO");
    }
    return 0;
}

int main_5_44(void) {
    int m, n;
    scanf("%d %d", &m, &n);
    int temp[n];
    for (int i = 0; i < n; i++) {
        for (int t = 0; t < n; t++) {
            scanf("%d", &temp[t]);
        }
        for (int t = n; t < 2 * n; t++) {
            printf("%d ", temp[(t - m % n) % n]);
        }
        printf("\n");
    }
    return 0;
}

int main_5_45(void) {
    int N, team[1001] = {0}, t, h, s, ans = 0;
    scanf("%d", &N);
    while (N--) {
        scanf("%d-%d %d", &t, &h, &s);
        team[t] += s;
        if (team[t] > team[ans]) {
            ans = t;
        }
    }
    printf("%d %d", ans, team[ans]);
    return 0;
}

int main_5_46(void) {
    char map[9];
    for (int i = 0; i < 9; i++) {
        scanf(" %c", &map[i]);
    }
    if (map[6] == map[7] && map[7] == map[8] || map[0] == map[3] && map[3] == map[6]) {
        if (map[6] != '.') {
            printf("%c win!", map[6]);
            goto jump;
        }
    }
    if (map[0] == map[1] && map[1] == map[2] || map[2] == map[5] && map[5] == map[8]) {
        if (map[2] != '.') {
            printf("%c win!", map[2]);
            goto jump;
        }
    }
    if (map[1] == map[4] && map[4] == map[7] || map[3] == map[4] && map[4] == map[5] ||
        map[0] == map[4] && map[4] == map[8] || map[2] == map[4] && map[4] == map[6]) {
        if (map[4] != '.') {
            printf("%c win!", map[4]);
        }
    }
    jump:
        printf("No one win!");
    return 0;
}

int main_5_47(void) {
    int N, max = 0, index = 0;
    scanf("%d", &N);
    char lst[N][81];
    for (int i = 0; i < N; i++) {
        scanf("%s", &lst[i]);
        int len = strlen(lst[i]);
        if (len > max) {
            max = len;
            index = i;
        }
    }
    printf("The longest is: %s", lst[index]);
    return 0;
}

int main_5_48(void) {
    char ch;
    while ((ch = getchar()) != '#') {
        if (ch >= 'a' && ch <= 'z') {
            ch -= 32;
        } else if (ch >= 'A' && ch <= 'Z') {
            ch += 32;
        }
        printf("%c", ch);
    }
    return 0;
}

int main_5_49(void) {
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
