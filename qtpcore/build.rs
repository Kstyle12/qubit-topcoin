fn main() {
    // Link against the installed RandomX library
    println!("cargo:rustc-link-lib=static=randomx");
    println!("cargo:rustc-link-search=/usr/local/lib");
    println!("cargo:rustc-link-lib=c++");
}
