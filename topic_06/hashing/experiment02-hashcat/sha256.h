#ifndef _SHA256_H
#define _SHA256_H

typedef struct sha256_ctx
{
  u32 h[8];

  u32 w0[4];
  u32 w1[4];
  u32 w2[4];
  u32 w3[4];

  int len;

} sha256_ctx_t;

//DECLSPEC void sha256_init (PRIVATE_AS sha256_ctx_t *ctx);

#endif // _SHA256_H