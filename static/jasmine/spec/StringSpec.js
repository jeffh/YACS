describe('String.format', function(){
  it('should return self if no args', function(){
    expect('foo'.format()).toEqual('foo');
  });

  it('should replace numbered args if first arg is not an object', function(){
    expect('foo {{ 0 }} bar {{ 1 }}'.format(1, 2)).toEqual('foo 1 bar 2');
  });

  it('should replace numbered args in one sweep', function(){
    expect('{{ 0 }}{{ 1 }}'.format('{{ 1 }}', '{{ 0 }}')).toEqual('{{ 1 }}{{ 0 }}');
  });

  it('should replace named args if first arg is an object', function(){
    expect('abc{{ foo }} {{ bar}};'.format({foo: 1, bar: 2})).toEqual('abc1 2;');
  });

  it('should replace named args in one sweep', function(){
    expect('abc{{ foo }} {{ bar }}'.format({foo: '{{ bar }}', bar: '{{ foo }}'})).toEqual('abc{{ bar }} {{ foo }}');
  });
});

describe('String.isBlank', function(){
  it('should return true if the string is empty', function(){
    expect(''.isBlank()).toBeTruthy();
  });

  it('should return true if the string has spaces', function(){
    expect('        '.isBlank()).toBeTruthy();
  });

  it('should return true if the string has tabs', function(){
    expect('\t  \t'.isBlank()).toBeTruthy();
  });

  it('should return false when having non-whitespace', function(){
    expect('  abc  '.isBlank()).toBeFalsy();
  });
});

describe('String.startsWith', function(){
  it('should return true if the string starts with substring', function(){
    expect('abcdefg'.startsWith('abc')).toBeTruthy();
  });

  it('should return false if the string does not start with substring', function(){
    expect('abcdefg'.startsWith('bcd')).toBeFalsy();
  });
});

describe('String.endsWith', function(){
  it('should return true if the string ends with substring', function(){
    expect('abcdefg'.endsWith('efg')).toBeTruthy();
  });

  it('should return false if the string does not end with substring', function(){
    expect('abcdefg'.endsWith('bcd')).toBeFalsy();
  });
});

describe('String.trim', function(){
  it('should return empty string if only whitespace', function(){
    expect('  \t \t \n'.trim()).toEqual('');
  });

  it('should return string with whitespace on sides removed', function(){
    expect(' \t\nabc\t \n'.trim()).toEqual('abc');
  });
});
