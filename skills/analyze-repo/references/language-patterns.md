# Language-Specific Pattern Registry

Based on the detected language(s), extract the relevant pattern sets from this registry. Include pattern sets for ALL detected languages in the CONTEXT block.

## JavaScript / TypeScript
```
debug: console.log, console.debug, debugger
type_suppress: @ts-ignore, @ts-expect-error, as any, // @ts-nocheck
lint_suppress: eslint-disable, eslint-disable-next-line, eslint-disable-line
unsafe: dangerouslySetInnerHTML, eval(, innerHTML =, document.write(
tests: *.test.*, *.spec.*, __tests__/
config: tsconfig*, .eslintrc*, .prettierrc*, biome.json, vite.config.*, next.config.*, webpack*
deps: package.json, package-lock.json, yarn.lock, pnpm-lock.yaml, bun.lockb
modules: export default, export {, module.exports, import
env_access: process.env., import.meta.env.
```

## Python
```
debug: print(, pdb.set_trace(), breakpoint(), ic(
type_suppress: # type: ignore, cast(Any, -> Any
lint_suppress: # noqa, # pylint: disable, # ruff: noqa, # flake8: noqa
unsafe: eval(, exec(, __import__(, |safe, mark_safe(, shell=True, subprocess.call(shell=
tests: test_*.py, *_test.py, conftest.py, tests/
config: pyproject.toml, setup.cfg, setup.py, .flake8, ruff.toml, mypy.ini, tox.ini
deps: pyproject.toml, requirements*.txt, Pipfile, poetry.lock
modules: from X import, import X, __init__.py, __all__
env_access: os.environ, os.getenv(, environ.get(
```

## Go
```
debug: fmt.Println, fmt.Printf, log.Println (in non-main packages)
type_suppress: interface{}, any (pre-1.18)
lint_suppress: //nolint, //nolint:specific
unsafe: unsafe.Pointer, #cgo, exec.Command(, sql.Query( without ?
tests: *_test.go
config: go.mod, go.sum, .golangci.yml
deps: go.mod, go.sum
modules: package X, func X, type X struct
env_access: os.Getenv(, os.LookupEnv(
```

## Rust
```
debug: println!, dbg!, eprintln!
type_suppress: #[allow(...)], as _, transmute
lint_suppress: #[allow(clippy::...)], #[allow(dead_code)], #[allow(unused
unsafe: unsafe {, unsafe fn, unsafe impl
tests: #[cfg(test)], tests/ directory
config: Cargo.toml, clippy.toml, rustfmt.toml
deps: Cargo.toml, Cargo.lock
modules: pub fn, pub struct, pub enum, pub mod, pub trait
env_access: env::var(, env::var_os(, std::env::
```

## Java
```
debug: System.out.println, System.err.println, e.printStackTrace()
type_suppress: @SuppressWarnings, (Object), raw types
lint_suppress: @SuppressWarnings, //CHECKSTYLE:OFF, //NOSONAR
unsafe: Runtime.exec(, PreparedStatement with string concat, @CrossOrigin(origins="*")
tests: *Test.java, *IT.java, src/test/
config: pom.xml, build.gradle, checkstyle.xml, spotbugs.xml
deps: pom.xml, build.gradle, build.gradle.kts
modules: public class, public interface, package
env_access: System.getenv(, @Value("${
```

## Ruby
```
debug: puts, p, pp, binding.pry, binding.irb, byebug
type_suppress: N/A (dynamically typed)
lint_suppress: # rubocop:disable
unsafe: eval, send(user_input), system(, `backticks`, html_safe, raw(
tests: *_spec.rb, *_test.rb, spec/, test/
config: Gemfile, .rubocop.yml, .ruby-version
deps: Gemfile, Gemfile.lock
modules: class X, module X, def X
env_access: ENV[, ENV.fetch(
```

## PHP
```
debug: var_dump, print_r, dd(, dump(, error_log
type_suppress: @, mixed, /** @var */
lint_suppress: // phpcs:ignore, // @codingStandardsIgnore
unsafe: eval(, exec(, system(, shell_exec(, {!! !!} (Blade), query( without bindings
tests: *Test.php, tests/
config: composer.json, phpstan.neon, .php-cs-fixer.php
deps: composer.json, composer.lock
modules: class X, namespace X, function X
env_access: env(, getenv(, $_ENV[
```

## Swift
```
debug: print(, debugPrint(, NSLog(, os_log
type_suppress: as!, force unwrap (!), Any
lint_suppress: // swiftlint:disable
unsafe: UnsafePointer, UnsafeMutablePointer, withUnsafe
tests: *Tests.swift, *Spec.swift
config: Package.swift, .swiftlint.yml
deps: Package.swift, Package.resolved, Podfile
modules: public func, public class, public struct, public protocol
env_access: ProcessInfo.processInfo.environment[
```

## Kotlin
```
debug: println(, Log.d(, Timber.d(
type_suppress: as, @Suppress, Any
lint_suppress: @Suppress, // ktlint-disable, detekt:off
unsafe: Runtime.exec(, ProcessBuilder, SQL string concat
tests: *Test.kt, *Spec.kt
config: build.gradle.kts, detekt.yml, .editorconfig
deps: build.gradle.kts, gradle.lockfile
modules: fun, class, object, interface, package
env_access: System.getenv(, BuildConfig.
```

## C# / .NET
```
debug: Console.WriteLine, Debug.WriteLine, Trace.WriteLine
type_suppress: dynamic, #pragma warning disable
lint_suppress: #pragma warning disable, [SuppressMessage(
unsafe: unsafe {, Process.Start(, SqlCommand with string concat
tests: *Tests.cs, *Test.cs, *.Tests/
config: *.csproj, *.sln, .editorconfig, Directory.Build.props
deps: *.csproj, packages.config, Directory.Packages.props
modules: public class, public interface, namespace
env_access: Environment.GetEnvironmentVariable(, IConfiguration[
```
