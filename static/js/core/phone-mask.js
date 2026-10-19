/**
 * PHONE-MASK.JS - Маска введення телефону для українських номерів
 * Формат: +38(___)__-__-___
 * Префікс +38 не можна видалити
 * Номер має починатися з 0 після +38
 */

class PhoneMask {
    constructor(input) {
        this.input = input;
        this.prefix = '+38';
        
        this.init();
    }

    init() {
        // КРИТИЧНО: Встановлюємо +38 завжди при ініціалізації
        this.ensurePrefix();
        
        // Прибираємо placeholder оскільки +38 завжди в полі
        if (this.input.placeholder) {
            this.input.setAttribute('data-original-placeholder', this.input.placeholder);
            this.input.placeholder = '';
        }
        
        // Додаємо +38 якщо поле порожнє при фокусі
        this.input.addEventListener('focus', () => this.handleFocus());
        
        // Обробка введення
        this.input.addEventListener('input', (e) => this.handleInput(e));
        
        // Заборона видалення +38
        this.input.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Обробка вставки (paste)
        this.input.addEventListener('paste', (e) => this.handlePaste(e));
        
        // Форматування при втраті фокусу
        this.input.addEventListener('blur', () => this.formatOnBlur());
        
        // Обробка виділення тексту - не дозволяти виділяти +38
        this.input.addEventListener('select', () => this.handleSelect());
        
        // Обробка reset форми - відновлюємо +38 після reset
        const form = this.input.closest('form');
        if (form) {
            form.addEventListener('reset', () => {
                // Використовуємо setTimeout щоб спрацювало після стандартного reset
                setTimeout(() => {
                    this.ensurePrefix();
                }, 0);
            });
        }
        
        // MutationObserver для відстеження змін значення ззовні
        this.setupValueObserver();
    }
    
    /**
     * Гарантує наявність префіксу +38 в полі
     */
    ensurePrefix() {
        const currentValue = this.input.value || '';
        
        // Якщо поле порожнє або не починається з +38, встановлюємо +38
        if (!currentValue.trim() || !currentValue.startsWith('+38')) {
            this.input.value = this.prefix;
            this.setCursorPosition(this.prefix.length);
        } else {
            // Якщо є значення з +38, форматуємо його
            this.formatValue(currentValue);
        }
    }
    
    /**
     * Налаштовує відстеження змін значення ззовні
     */
    setupValueObserver() {
        // Відстежуємо зміни значення через setInterval
        let lastValue = this.input.value;
        let isActive = true;
        
        // Перевіряємо зміни значення через setInterval (більш надійно ніж MutationObserver для input.value)
        this.valueCheckInterval = setInterval(() => {
            if (!isActive) return;
            
            const currentValue = this.input.value;
            
            // Якщо значення змінилося ззовні і не починається з +38
            if (currentValue !== lastValue) {
                lastValue = currentValue;
                
                // Якщо значення порожнє або не починається з +38, відновлюємо префікс
                if (!currentValue || !currentValue.trim() || !currentValue.startsWith('+38')) {
                    this.ensurePrefix();
                    lastValue = this.input.value;
                }
            }
        }, 100);
        
        // Зупиняємо перевірку при blur (не перезапускаємо, щоб уникнути накопичення інтервалів)
        const blurHandler = () => {
            isActive = false;
        };
        
        // Відновлюємо перевірку при focus
        const focusHandler = () => {
            isActive = true;
            lastValue = this.input.value;
        };
        
        this.input.addEventListener('blur', blurHandler);
        this.input.addEventListener('focus', focusHandler);
        
        // Зберігаємо обробники для можливості очищення
        this._valueObserverHandlers = { blur: blurHandler, focus: focusHandler };
    }

    handleFocus() {
        // Переконуємось що +38 завжди присутнє при фокусі
        const currentValue = this.input.value;
        if (!currentValue || currentValue.trim() === '' || !currentValue.startsWith('+38')) {
            this.input.value = this.prefix;
            this.setCursorPosition(this.prefix.length);
        } else {
            // Якщо +38 є, переконуємось що курсор не перед ним
            const cursorPos = this.input.selectionStart;
            if (cursorPos < this.prefix.length) {
                this.setCursorPosition(this.prefix.length);
            }
        }
    }

    handleInput(e) {
        let value = this.input.value;
        
        // Зберігаємо позицію курсора та виділення
        const cursorPos = this.input.selectionStart;
        const selectionEnd = this.input.selectionEnd;
        
        // Підраховуємо скільки цифр було перед курсором (включаючи префікс 38)
        const textBeforeCursor = value.substring(0, cursorPos);
        const allDigitsBeforeCursor = textBeforeCursor.replace(/[^\d]/g, '').length;
        
        // Рахуємо тільки цифри після префіксу 38 (включаючи 0 якщо є)
        // Якщо є префікс 38, то віднімаємо 2, інакше залишаємо як є
        const digitsAfterPrefix = allDigitsBeforeCursor >= 2 ? allDigitsBeforeCursor - 2 : 0;
        
        // Видаляємо все крім цифр та +
        let cleaned = value.replace(/[^\d+]/g, '');
        
        // КРИТИЧНО: Переконуємось що ЗАВЖДИ починається з +38
        if (!cleaned.startsWith('+38')) {
            if (cleaned.startsWith('38')) {
                cleaned = '+' + cleaned;
            } else if (cleaned.startsWith('8')) {
                cleaned = '+38' + cleaned.substring(1);
            } else if (cleaned.match(/^\d/)) {
                cleaned = '+38' + cleaned;
            } else if (cleaned.startsWith('+')) {
                // Якщо є + але не +38, замінюємо на +38
                cleaned = '+38' + cleaned.substring(1).replace(/[^\d]/g, '');
            } else {
                cleaned = '+38' + cleaned.replace(/[^\d]/g, '');
            }
        }
        
        // Обмежуємо довжину (максимум 12 цифр після +38, тобто +38 + 10 цифр номера)
        const digits = cleaned.replace(/\D/g, '');
        if (digits.length > 12) {
            cleaned = '+38' + digits.substring(2, 12); // Беремо тільки цифри після 38
        }
        
        // Форматуємо значення
        this.formatValue(cleaned);
        
        // КРИТИЧНО: Переконуємось що +38 завжди присутнє після форматування
        setTimeout(() => {
            if (!this.input.value.startsWith('+38')) {
                this.input.value = this.prefix + (this.input.value || '');
                this.formatValue(this.input.value);
            }
            
            // Розраховуємо нову позицію курсора на основі кількості цифр після префіксу
            // Враховуємо форматування: +38(0XX)XX-XX-XXX
            const newCursorPos = this.calculateCursorPosition(digitsAfterPrefix);
            this.setCursorPosition(newCursorPos);
        }, 0);
    }
    
    /**
     * Розраховує позицію курсора після форматування на основі кількості цифр після префіксу 38
     * @param {number} digitsAfterPrefix - кількість цифр після префіксу 38 (0-10)
     * @returns {number} - нова позиція курсора
     */
    calculateCursorPosition(digitsAfterPrefix) {
        // Префікс +38 завжди присутній (3 символи)
        if (digitsAfterPrefix === 0) {
            // Тільки префікс +38, курсор після нього
            return 3;
        }
        
        // Після +38 йде дужка "(" і перші цифри
        if (digitsAfterPrefix <= 3) {
            // +38(0, +38(0X, +38(0XX
            // +38 + ( + цифри
            return 3 + 1 + digitsAfterPrefix; // +38 + ( + цифри
        }
        
        // Після 3 цифр йде дужка ")"
        if (digitsAfterPrefix <= 5) {
            // +38(0XX)X, +38(0XX)XX
            // +38 + ( + 3 цифри + ) + решта
            return 3 + 1 + 3 + 1 + (digitsAfterPrefix - 3); // +38 + ( + 3 + ) + решта
        }
        
        // Після 5 цифр йде дефіс "-"
        if (digitsAfterPrefix <= 7) {
            // +38(0XX)XX-X, +38(0XX)XX-XX
            // +38 + ( + 3 + ) + 2 + - + решта
            return 3 + 1 + 3 + 1 + 2 + 1 + (digitsAfterPrefix - 5); // +38 + ( + 3 + ) + 2 + - + решта
        }
        
        // Після 7 цифр йде другий дефіс "-"
        if (digitsAfterPrefix <= 9) {
            // +38(0XX)XX-XX-X, +38(0XX)XX-XX-XX
            // +38 + ( + 3 + ) + 2 + - + 2 + - + решта
            return 3 + 1 + 3 + 1 + 2 + 1 + 2 + 1 + (digitsAfterPrefix - 7); // +38 + ( + 3 + ) + 2 + - + 2 + - + решта
        }
        
        // Після 9 цифр (максимум 10)
        if (digitsAfterPrefix <= 10) {
            // +38(0XX)XX-XX-XXX
            // +38 + ( + 3 + ) + 2 + - + 2 + - + решта (3 цифри для повного номера)
            if (digitsAfterPrefix <= 9) {
                // +38(0XX)XX-XX-XX (9 цифр після префіксу)
                return 3 + 1 + 3 + 1 + 2 + 1 + 2 + 1 + (digitsAfterPrefix - 7); // +38 + ( + 3 + ) + 2 + - + 2 + - + решта
            } else {
                // +38(0XX)XX-XX-XXX (10 цифр після префіксу - повний номер)
                return 3 + 1 + 3 + 1 + 2 + 1 + 2 + 1 + 3; // +38 + ( + 3 + ) + 2 + - + 2 + - + 3
            }
        }
        
        // Максимум - в кінці
        return this.input.value.length;
    }

    handleKeyDown(e) {
        const cursorPos = this.input.selectionStart;
        const selectionEnd = this.input.selectionEnd;
        const value = this.input.value;
        
        // Заборона видалення +38
        if (e.key === 'Backspace' || e.key === 'Delete') {
            // Якщо виділення включає +38 або курсор перед +38, блокуємо видалення
            if (cursorPos < this.prefix.length || (selectionEnd > 0 && selectionEnd <= this.prefix.length)) {
                e.preventDefault();
                // Переконуємось що +38 завжди присутнє
                if (!value.startsWith('+38')) {
                    this.input.value = this.prefix + (value.substring(this.prefix.length) || '');
                }
                this.setCursorPosition(this.prefix.length);
                return;
            }
            
            // Якщо користувач намагається видалити частину +38, блокуємо
            if (cursorPos > 0 && cursorPos <= this.prefix.length) {
                e.preventDefault();
                this.setCursorPosition(this.prefix.length);
                return;
            }
        }
        
        // Заборона вставки курсору перед +38
        if (e.key === 'ArrowLeft' && cursorPos <= this.prefix.length) {
            e.preventDefault();
            this.setCursorPosition(this.prefix.length);
        }
        
        // Заборона вирізання +38
        if ((e.ctrlKey || e.metaKey) && e.key === 'x') {
            if (cursorPos < this.prefix.length || selectionEnd <= this.prefix.length) {
                e.preventDefault();
            }
        }
        
        // Заборона виділення +38 через Shift+ArrowLeft
        if (e.shiftKey && e.key === 'ArrowLeft' && cursorPos <= this.prefix.length) {
            e.preventDefault();
            this.setCursorPosition(this.prefix.length);
        }
    }

    handlePaste(e) {
        // Do NOT call e.preventDefault() — browsers flag paste-blocking as a UX issue.
        // Allow the native paste, then reformat in the next microtask.
        const pastedText = (e.clipboardData ?? window.clipboardData).getData('text');

        setTimeout(() => {
            let cleaned = pastedText.replace(/[^\d+]/g, '');

            if (!cleaned.startsWith('+38')) {
                if (cleaned.startsWith('38')) {
                    cleaned = '+' + cleaned;
                } else if (cleaned.startsWith('8')) {
                    cleaned = '+38' + cleaned.substring(1);
                } else if (/^\d/.test(cleaned)) {
                    cleaned = '+38' + cleaned;
                } else {
                    cleaned = '+38' + cleaned.replace(/[^\d]/g, '');
                }
            }

            const digits = cleaned.replace(/\D/g, '');
            if (digits.length > 12) {
                cleaned = '+38' + digits.substring(2, 12);
            }

            this.formatValue(cleaned);
            this.setCursorPosition(Math.max(this.prefix.length, this.input.value.length));
        }, 0);
    }

    formatValue(value) {
        // Якщо value порожнє або undefined, встановлюємо +38
        if (!value || typeof value !== 'string') {
            this.input.value = this.prefix;
            return;
        }
        
        // Видаляємо все крім цифр та +
        let digits = value.replace(/[^\d]/g, '');
        
        // КРИТИЧНО: Переконуємось що ЗАВЖДИ починається з 38
        if (!digits.startsWith('38')) {
            if (digits.startsWith('8')) {
                digits = '38' + digits.substring(1);
            } else {
                digits = '38' + digits;
            }
        }
        
        // Обмежуємо до 12 цифр (38 + 10 цифр номера)
        if (digits.length > 12) {
            digits = digits.substring(0, 12);
        }
        
        // Зберігаємо мінімум +38 навіть якщо немає цифр
        if (digits.length < 2) {
            digits = '38';
        }
        
        // Форматуємо: +38(0XX)XX-XX-XXX
        // ЗАВЖДИ починаємо з +38
        // digits містить: 38 + 10 цифр номера (0 + ще 9) = 12 цифр максимум
        let formatted = '';
        if (digits.length <= 2) {
            formatted = '+' + digits; // +38
        } else if (digits.length <= 5) {
            // +38(0XX) - 3-5 цифр (38 + 1-3 цифри після)
            formatted = '+' + digits.substring(0, 2) + '(' + digits.substring(2);
        } else if (digits.length <= 7) {
            // +38(0XX)XX - 6-7 цифр (38 + 4-5 цифр після)
            formatted = '+' + digits.substring(0, 2) + '(' + digits.substring(2, 5) + ')' + digits.substring(5);
        } else if (digits.length <= 9) {
            // +38(0XX)XX-XX - 8-9 цифр (38 + 6-7 цифр після)
            formatted = '+' + digits.substring(0, 2) + '(' + digits.substring(2, 5) + ')' + digits.substring(5, 7) + '-' + digits.substring(7);
        } else if (digits.length <= 11) {
            // +38(0XX)XX-XX-XX - 10-11 цифр (38 + 8-9 цифр після)
            formatted = '+' + digits.substring(0, 2) + '(' + digits.substring(2, 5) + ')' + digits.substring(5, 7) + '-' + digits.substring(7, 9) + '-' + digits.substring(9);
        } else {
            // +38(0XX)XX-XX-XXX - 12 цифр (38 + 10 цифр після) - ПОВНИЙ НОМЕР
            formatted = '+' + digits.substring(0, 2) + '(' + digits.substring(2, 5) + ')' + digits.substring(5, 7) + '-' + digits.substring(7, 9) + '-' + digits.substring(9, 12);
        }
        
        // КРИТИЧНО: Переконуємось що +38 завжди присутнє
        if (!formatted.startsWith('+38')) {
            formatted = this.prefix;
        }
        
        this.input.value = formatted;
        
        // Додаткова перевірка після встановлення значення
        if (!this.input.value.startsWith('+38')) {
            this.input.value = this.prefix;
        }
    }

    formatOnBlur() {
        const value = this.input.value;
        // Переконуємось що +38 завжди присутнє
        if (!value || value.trim() === '' || !value.startsWith('+38')) {
            this.input.value = this.prefix;
        } else {
            this.formatValue(value);
        }
    }
    
    handleSelect() {
        // Не дозволяємо виділяти +38
        const selectionStart = this.input.selectionStart;
        const selectionEnd = this.input.selectionEnd;
        
        if (selectionStart < this.prefix.length || selectionEnd <= this.prefix.length) {
            // Якщо виділення включає +38, змінюємо виділення
            setTimeout(() => {
                if (selectionStart < this.prefix.length) {
                    this.input.setSelectionRange(this.prefix.length, Math.max(this.prefix.length, selectionEnd));
                }
            }, 0);
        }
    }

    setCursorPosition(position) {
        // Використовуємо setTimeout для коректної встановки позиції
        setTimeout(() => {
            this.input.setSelectionRange(position, position);
        }, 0);
    }

    /**
     * Валідація номера телефону
     * @returns {Object} {valid: boolean, message: string}
     */
    validate() {
        const value = this.input.value;

        if (!value || value.trim() === '' || value === this.prefix) {
            return {
                valid: false,
                message: window.I18N?.phoneRequired || (((document.documentElement.getAttribute('lang') || 'cs').toLowerCase().indexOf('en') === 0) ? 'Enter a valid phone number.' : 'Zadejte platné telefonní číslo.')
            };
        }

        const digits = value.replace(/\D/g, '');
        if (digits.length < 7) {
            return {
                valid: false,
                message: window.I18N?.phoneInvalid || (((document.documentElement.getAttribute('lang') || 'cs').toLowerCase().indexOf('en') === 0) ? 'Enter a valid phone number.' : 'Zadejte platné telefonní číslo.')
            };
        }

        return {
            valid: true,
            message: '',
            cleaned: value.replace(/[^\d+]/g, '')
        };
    }

    /**
     * Отримати очищене значення для відправки
     * @returns {string}
     */
    getCleanedValue() {
        const value = this.input.value;
        return value.replace(/[^\d+]/g, '');
    }
    
    /**
     * Очищення ресурсів (викликати при видаленні об'єкта)
     */
    destroy() {
        if (this.valueCheckInterval) {
            clearInterval(this.valueCheckInterval);
            this.valueCheckInterval = null;
        }
        
        // Видаляємо обробники подій
        if (this._valueObserverHandlers) {
            this.input.removeEventListener('blur', this._valueObserverHandlers.blur);
            this.input.removeEventListener('focus', this._valueObserverHandlers.focus);
            this._valueObserverHandlers = null;
        }
    }
}

// Експорт для використання в інших модулях
if (typeof window !== 'undefined') {
    window.PhoneMask = PhoneMask;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = PhoneMask;
}

