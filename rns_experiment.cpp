#include <iostream>
#include <vector>
#include <cstdint>

using namespace std;

class RNS {
private:
    vector<int64_t> moduli;
    vector<int64_t> S;
    int64_t P_work, P_full, P_control;
    
    int64_t modInverse(int64_t a, int64_t m) {
        int64_t m0 = m, y = 0, x = 1;
        while (a > 1) {
            int64_t q = a / m, t = m;
            m = a % m, a = t;
            t = y, y = x - q * y, x = t;
        }
        return x < 0 ? x + m0 : x;
    }
    
    void computeS() {
        int n = moduli.size();
        S.resize(n);
        for (int i = 0; i < n; ++i) {
            int64_t Mi = P_full / moduli[i];
            int64_t inv = modInverse(Mi, moduli[i]);
            int64_t Bi = Mi * inv;
            S[i] = (Bi - (Bi % P_work)) / P_work;
        }
    }
    
public:
    void setup() {
        moduli = {1009, 1013, 1019, 1021, 1031};
        P_work = 1009 * 1013 * 1019;
        P_full = P_work * 1021 * 1031;
        P_control = 1021 * 1031;
        computeS();
    }
    
    vector<int64_t> encrypt(int64_t num) {
        // Нормализация
        int64_t norm = num % P_work;
        if (norm < 0) norm += P_work;
        
        // ВЫЧИСЛЯЕМ ОСТАТКИ!
        vector<int64_t> res(5);
        for (int i = 0; i < 5; ++i) {
            res[i] = norm % moduli[i];  // <-- ЭТО КЛЮЧЕВОЕ!
        }
        return res;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) return 1;
    
    RNS rns;
    rns.setup();
    
    int64_t num = atoll(argv[1]);
    vector<int64_t> res = rns.encrypt(num);
    
    for (int i = 0; i < 5; ++i) {
        cout << res[i] << (i < 4 ? " " : "");
    }
    cout << endl;
    
    return 0;
}