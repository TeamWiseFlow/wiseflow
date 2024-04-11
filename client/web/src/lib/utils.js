import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatDate(date) {
  var d = new Date(isNaN(date) ? date + "T00:00:00" : date)
  var iso = d.toISOString()
  return iso.slice(0, 10) + " " + iso.slice(11, 23) + "Z"
  // return [d.getFullYear(), (d.getMonth() + 1).padLeft(), d.getDate().padLeft()].join("-") + " " + [d.getHours().padLeft(), d.getMinutes().padLeft(), d.getSeconds().padLeft()].join(":") + ".000Z"
}

Number.prototype.padLeft = function (base, chr) {
  var len = String(base || 10).length - String(this).length + 1
  return len > 0 ? new Array(len).join(chr || "0") + this : this
}
