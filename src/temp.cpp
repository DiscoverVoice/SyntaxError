#include <iostream>
#include <set>
#include <vector>

using namespace std;

int main() {
    int N, M, K;
    cin >> N >> M >> K;

    set<int> blue_cards;
    
    for (int i = 0; i < M; ++i) {
        int card;
        cin >> card;
        blue_cards.insert(card);
    }

    vector<int> chulsoo_cards(K);
    for (int i = 0; i < K; ++i) {
        cin >> chulsoo_cards[i];
    }

    for (int i = 0; i < K; ++i) {
        int chulsoo_card = chulsoo_cards[i];
        
        auto it = blue_cards.upper_bound(chulsoo_card);
        
        if (it != blue_cards.end()) {
            cout << *it << endl;
            blue_cards.erase(it);
        }
    }

    return 0;
}
