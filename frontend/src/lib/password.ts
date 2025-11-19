const encoder = new TextEncoder();

export const PASSWORD_MAX_BYTES = 72;

export function truncatePassword(input: string, maxBytes: number = PASSWORD_MAX_BYTES): {
  password: string;
  truncated: boolean;
} {
  let result = input;
  if (encoder.encode(result).length <= maxBytes) {
    return { password: result, truncated: false };
  }

  let low = 0;
  let high = result.length;
  while (low < high) {
    const mid = Math.floor((low + high) / 2);
    const slice = input.slice(0, mid);
    const size = encoder.encode(slice).length;
    if (size <= maxBytes) {
      result = slice;
      low = mid + 1;
    } else {
      high = mid;
    }
  }

  while (encoder.encode(result).length > maxBytes && result.length > 0) {
    result = result.slice(0, -1);
  }

  return { password: result, truncated: true };
}
