#include "types.h"
#include "sha256.h"

kernel void sha256_init (global sha256_ctx_t *ctx)
{
  ctx->h[0] = SHA256M_A;
  ctx->h[1] = SHA256M_B;
  ctx->h[2] = SHA256M_C;
  ctx->h[3] = SHA256M_D;
  ctx->h[4] = SHA256M_E;
  ctx->h[5] = SHA256M_F;
  ctx->h[6] = SHA256M_G;
  ctx->h[7] = SHA256M_H;

  ctx->w0[0] = 0;
  ctx->w0[1] = 0;
  ctx->w0[2] = 0;
  ctx->w0[3] = 0;
  ctx->w1[0] = 0;
  ctx->w1[1] = 0;
  ctx->w1[2] = 0;
  ctx->w1[3] = 0;
  ctx->w2[0] = 0;
  ctx->w2[1] = 0;
  ctx->w2[2] = 0;
  ctx->w2[3] = 0;
  ctx->w3[0] = 0;
  ctx->w3[1] = 0;
  ctx->w3[2] = 0;
  ctx->w3[3] = 0;

  ctx->len = 0;
}