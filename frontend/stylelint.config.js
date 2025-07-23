module.exports = {
  extends: ['stylelint-config-standard'],
  rules: {
    'at-rule-no-unknown': [
      true,
      {
        ignoreAtRules: [
          'tailwind',
          'apply',
          'variants',
          'responsive',
          'screen',
        ],
      },
    ],
    'declaration-block-trailing-semicolon': null,
    'no-descending-specificity': null,
    'keyframes-name-pattern': null,
    'selector-class-pattern': null,
    'property-no-unknown': null,
    'no-duplicate-selectors': null,
    'declaration-block-single-line-max-declarations': null,
    'no-invalid-double-slash-comments': null,
  },
};
