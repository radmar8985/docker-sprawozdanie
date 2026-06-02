# Sprawozdanie z Zadania 2: CI/CD oraz Bezpieczeństwo Obrazów

Celem zadania było wdrożenie zautomatyzowanego łańcucha budowania obrazu z Zadania 1 z użyciem GitHub Actions. Wymagania obejmowały wsparcie dla wielu architektur (amd64, arm64), zewnętrzny system cache z trybem `max` na DockerHub oraz obowiązkowy test CVE skanerem bezpieczeństwa.

## Zrealizowane kroki i konfiguracja

1. **Wsparcie dla wielu architektur:**
   Rozwiązano to za pomocą akcji `docker/setup-qemu-action` i technologii emulatora QEMU. Budowanie docelowe `docker/build-push-action` ma ustawiony parametr `platforms: linux/amd64,linux/arm64`.

2. **Zarządzanie Cache:**
   Użyto publicznego repozytorium na DockerHub jako zewnętrznego miejsca do składowania artefaktów cache'ujących.
   Skonfigurowano parametry pod akcją budowania:
   - `cache-from: type=registry,ref=<user>/app-pogoda-cache:buildcache`
   - `cache-to: type=registry,ref=<user>/app-pogoda-cache:buildcache,mode=max`
   
3. **Skaner Podatności (Trivy):**
   Użyto skanera Trivy marki Aqua Security (akcja `aquasecurity/trivy-action`). Łańcuch posiada dedykowany krok ładujący najpierw obraz w formie lokalnej (`load: true`), co pozwala Trivy wejść w strukturę wewnętrzną przed publikacją obrazu. W przypadku wykrycia błędów o randze `CRITICAL` lub `HIGH`, Trivy zwraca kod błędu (`exit-code: 1`), co natychmiast przerywa działanie łańcucha GitHub Actions i zabezpiecza GHCR przed przyjęciem dziurawego obrazu.

## Strategia Tagowania

**Obrazy publikowane na GHCR:**
Tagowane są wieloma etykietami na raz (wygenerowane przez `docker/metadata-action`):
- `latest` - w celu łatwego pobrania w fazie testowej na środowiskach developerskich.
- `sha-<hash commitu>` - identyfikator commita chroniący przed cichym nadpisaniem binarnego kształtu aplikacji. To elementarne bezpieczeństwo z dziedziny dostarczania oprogramowania (GitOps), który pozwala bezpośrednio połączyć konkretny kontener operacyjny ze stanem drzewa z systemu kontroli wersji.

**Obrazy Cache publikowane na DockerHub:**
Eksport odbywa się do unikalnego tagu `:buildcache`. Jest to świadomy wybór architektoniczny – w rejestrze oddzielono "śmieci i pliki pośrednie z buildera" od produkcyjnego, uruchomieniowego obrazu kontenera trzymanego na GitHub Packages.