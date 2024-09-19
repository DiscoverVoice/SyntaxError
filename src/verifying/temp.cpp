#include <iostream>
#include <vector>
using namespace std;

const int MAX_N = 4000005;

int N, M, K;
int parent[MAX_N];
bool available[MAX_N];

int find(int x) {
  if (x > N + 1) return N + 1;
  if (parent[x] != x) {
    parent[x] = find(parent[x]);
    return parent[x];
  } else {
    if (available[x]) {
      return x;
    } else {
      parent[x] = find(x + 1);
      return parent[x];
    }
  }
}

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);

  cin >> N >> M >> K;

  for (int i = 1; i <= N + 2; ++i) {
    parent[i] = i;
    available[i] = false;
  }

  for (int i = 0; i < M; ++i) {
    int card;
    cin >> card;
    available[card] = true;
  }

  vector<int> cheolsu_cards(K);
  for (int i = 0; i < K; ++i) {
    cin >> cheolsu_cards[i];
  }

  for (int i = 0; i < K; ++i) {
    int c = cheolsu_cards[i];
    int minsus_card = find(c + 1);
    cout << minsus_card << '\n';
    available[minsus_card] = false;
    parent[minsus_card] = minsus_card + 1;
  }

  return 0;
}
