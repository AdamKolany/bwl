      function prettyPrimes(latex) {
       return latex
        .replace(/\^\{\\prime\\prime\\prime\}/g, "'''")
        .replace(/\^\{\\prime\\prime\}/g, "''")
        .replace(/\^\{\\prime\}/g, "'")
        .replace(/\^\\prime/g, "'");
      }

      function prettyPrimesForDisplay(latex) {
       return latex
	.replace(/\^\{\\prime\\prime\\prime\}/g, "\u2034")
	.replace(/\^\{\\prime\\prime\}/g, "\u2033")
	.replace(/\^\{\\prime\}/g, "\u2032")
	.replace(/\^\\prime/g, "\u2032");
      }