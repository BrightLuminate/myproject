document.addEventListener('DOMContentLoaded', function() {
    // 숫자를 플립하는 함수
    function animateDigits(digits, targetNumber) {
        digits.forEach((digit, index) => {
            const topHalf = digit.querySelector('.flip-top');
            const bottomHalf = digit.querySelector('.flip-bottom');

            const currentDigit = digit.innerText.trim();

            // 목표 숫자의 각 자릿수 가져오기
            let targetDigit = targetNumber[index];

            if (currentDigit !== targetDigit) {
                bottomHalf.innerText = targetDigit;
                digit.classList.add('flipping');
                setTimeout(() => {
                    topHalf.innerText = targetDigit;
                    bottomHalf.innerText = currentDigit;
                    digit.classList.remove('flipping');
                }, 500); // 플립 애니메이션 지속 시간
            }
        });
    }

    // 초기 설정
    const digits = document.querySelectorAll('.flip-clock .digit');
    const targetNumber = '5000'.split(''); // 목표 숫자를 각 자릿수 배열로 변환
    animateDigits(digits, targetNumber);
});
