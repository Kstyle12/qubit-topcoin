use std::ffi::c_void;

// Raw FFI bindings to the RandomX C library
#[allow(non_camel_case_types)]
type randomx_cache   = c_void;
#[allow(non_camel_case_types)]
type randomx_dataset = c_void;
#[allow(non_camel_case_types)]
type randomx_vm      = c_void;

#[repr(u32)]
#[allow(dead_code)]
pub enum RandomXFlags {
    Default    = 0,
    LargePages = 1,
    HardAes    = 2,
    FullMem    = 4,
    Jit        = 8,
    Secure     = 16,
    Argon2Ssse3 = 32,
    Argon2Avx2  = 64,
    Argon2      = 96,
}

extern "C" {
    fn randomx_alloc_cache(flags: u32) -> *mut randomx_cache;
    fn randomx_init_cache(
        cache: *mut randomx_cache,
        key:   *const u8,
        keySize: usize,
    );
    fn randomx_release_cache(cache: *mut randomx_cache);
    fn randomx_create_vm(
        flags:   u32,
        cache:   *mut randomx_cache,
        dataset: *mut randomx_dataset,
    ) -> *mut randomx_vm;
    fn randomx_destroy_vm(machine: *mut randomx_vm);
    fn randomx_calculate_hash(
        machine: *mut randomx_vm,
        input:   *const u8,
        inputSize: usize,
        output:  *mut u8,
    );
}

pub struct RandomXHasher {
    cache: *mut randomx_cache,
    vm:    *mut randomx_vm,
}

impl RandomXHasher {
    pub fn new(key: &[u8]) -> Self {
        unsafe {
            let flags = RandomXFlags::Default as u32;
            let cache = randomx_alloc_cache(flags);
            randomx_init_cache(cache, key.as_ptr(), key.len());
            let vm = randomx_create_vm(flags, cache, std::ptr::null_mut());
            RandomXHasher { cache, vm }
        }
    }

    pub fn hash(&self, input: &[u8]) -> [u8; 32] {
        let mut output = [0u8; 32];
        unsafe {
            randomx_calculate_hash(
                self.vm,
                input.as_ptr(),
                input.len(),
                output.as_mut_ptr(),
            );
        }
        output
    }
}

impl Drop for RandomXHasher {
    fn drop(&mut self) {
        unsafe {
            randomx_destroy_vm(self.vm);
            randomx_release_cache(self.cache);
        }
    }
}

// Check if a RandomX hash meets difficulty target
pub fn meets_difficulty(hash: &[u8; 32], difficulty: usize) -> bool {
    let target = "0".repeat(difficulty);
    let hash_hex = hex::encode(hash);
    hash_hex.starts_with(&target)
}
