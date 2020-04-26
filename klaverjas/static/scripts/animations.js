const Animations = {};


(function() {
    let active = false;
    const animations = [];

    const tick = function() {
        if (!animations.length) {
            active = false;
            return;
        }

        const now = performance.now();

        for (let i = 0; i < animations.length; i++) {
            const animation = animations[i];

            if (now < animation.start) {
                continue;
            }

            if (!animation.active) {
                animation.active = true;
                if (animation.on_start) {
                    animation.on_start();
                }
            }

            const delta = (now - animation.start) / animation.duration;
            animation.on_progress(animation.effect(Math.min(delta, 1)));

            if (now > animation.end) {
                animations.splice(i--, 1);
                if (animation.on_end) {
                    animation.on_end();
                }
            }
        }

        window.requestAnimationFrame(tick);
    };


    Animations.effects = {
        ease: function(t) {
            return t < 0.5 ? 4 * t * t * t :
                             (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
        },

        linear: function(t) {
            return t;
        }
    };

    Animations.create = function(duration, on_progress, params) {
        const now = performance.now();
        const start = now + (params.delay || 0);

        animations.push({
            start: start,
            end: start + duration,
            duration: duration,
            on_start: params.on_start,
            on_progress: on_progress,
            on_end: params.on_end,
            effect: params.effect || Animations.effects.linear
        });

        if (!active) {
            active = true;
            window.requestAnimationFrame(tick);
        }
    };
})();


export {
    Animations
}
