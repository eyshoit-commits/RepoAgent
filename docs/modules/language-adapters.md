# Language Adapters

The `config/languages.yaml` file defines compilation or execution commands per language. Each entry specifies
an identifier, runtime tooling, and a verification command that can be invoked by external orchestrators.

Example entry:

```yaml
- id: java
  name: Java 21
  build: mvn -q -DskipTests package
  run: java -jar target/app.jar
  verify: mvn -q test
```

The CLI surfaces this metadata so you can plug it into CI/CD pipelines or developer automation.
