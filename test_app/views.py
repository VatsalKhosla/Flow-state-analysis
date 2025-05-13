from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
import random
from .models import TestSession, StateAttempt, QuestionAttempt

class CognitiveTestView(View):

    SEQUENCES = [
        ['R', 'B', 'F', 'O', 'F', 'R', 'O', 'B', 'O', 'B', 'F', 'R'],
        ['R', 'B', 'O', 'F', 'O', 'R', 'F', 'B', 'F', 'B', 'O', 'R']
    ]

    def generate_arithmetic_question(self, difficulty_level, state):
        """
        Generate arithmetic questions based on difficulty and state
        """
        if state == 'B':  
            num1 = random.randint(100, 109)
            num2 = random.randint(1, 9)
            question = f"{num1} + {num2}"
            answer = num1 + num2
            return question, str(answer)
        
        elif state == 'F': 
            if difficulty_level == 1:
                # 3 two-digit numbers
                nums = [random.randint(10, 99) for _ in range(3)]
                question = " + ".join(map(str, nums))
                answer = sum(nums)
            else:
                # Slightly more complex as difficulty increases
                nums = [random.randint(10, 99) for _ in range(3 + difficulty_level - 1)]
                question = " + ".join(map(str, nums))
                answer = sum(nums)
            return question, str(answer)
        
        elif state == 'O':  
            # 4 two-digit numbers difficulty increases
            nums = [random.randint(10, 99) for _ in range(4 + difficulty_level - 1)]
            question = " + ".join(map(str, nums))
            answer = sum(nums)
            return question, str(answer)
        
        return "", ""

    def start_test(self, request):
       
        session = TestSession.objects.create(
            current_sequence=1,
            current_state=self.SEQUENCES[0][0]
        )
        return redirect('test_state', session_id=session.id, state=session.current_state)

    def start_second_sequence(self, request):
     
        session = TestSession.objects.create(
            current_sequence=2,
            current_state=self.SEQUENCES[1][0]
        )
        return redirect('test_state', session_id=session.id, state=session.current_state)

    def test_state(self, request, session_id, state):
   
        session = TestSession.objects.get(id=session_id)
        
       
        state_attempt = StateAttempt.objects.create(
            session=session,
            state=state,
            difficulty_level=1  # Start with default difficulty
        )

        context = {
            'session_id': session_id,
            'state': state,
            'sequence': session.current_sequence
        }


        if state == 'R':  
            return render(request, 'test_app/resting_state.html', context)
        
        elif state == 'B':
         
            question, correct_answer = self.generate_arithmetic_question(1, 'B')
            context['question'] = question
            context['state_attempt_id'] = state_attempt.id
            return render(request, 'test_app/bored_state.html', context)
        
        elif state == 'F': 

            question, correct_answer = self.generate_arithmetic_question(1, 'F')
            context['question'] = question
            context['state_attempt_id'] = state_attempt.id
            return render(request, 'test_app/flow_state.html', context)
        
        elif state == 'O': 

            question, correct_answer = self.generate_arithmetic_question(1, 'O')
            context['question'] = question
            context['state_attempt_id'] = state_attempt.id
            return render(request, 'test_app/overload_state.html', context)

    def submit_answer(self, request, session_id, state_attempt_id):
       
        if request.method == 'POST':
          
            session = TestSession.objects.get(id=session_id)
            state_attempt = StateAttempt.objects.get(id=state_attempt_id)
            
            # Get form data
            user_answer = request.POST.get('answer', '')
            current_question = request.POST.get('question', '')
            remaining_time = request.POST.get('remaining_time', '0')
            
            # Convert remaining_time to integer default to 0 if invalid
            try:
                remaining_time = int(remaining_time)
            except (ValueError, TypeError):
                remaining_time = 0
                
            # Generate question and correct answer
            _, correct_answer = self.generate_arithmetic_question(
                state_attempt.difficulty_level, 
                state_attempt.state
            )
            
            # Create question attempt
            attempt = QuestionAttempt.objects.create(
                state_attempt=state_attempt,
                question=current_question,
                answer=user_answer,
                correct_answer=correct_answer,
                is_correct=user_answer == correct_answer
            )

            # Adjust difficulty based on state-specific rules
            if state_attempt.state == 'F':
                
                recent_attempts = QuestionAttempt.objects.filter(
                    state_attempt=state_attempt
                ).order_by('-timestamp')[:2]
                
                if len(recent_attempts) == 2:
                    if all(attempt.is_correct for attempt in recent_attempts):
                        state_attempt.difficulty_level += 1
                    elif all(not attempt.is_correct for attempt in recent_attempts):
                        state_attempt.difficulty_level = max(1, state_attempt.difficulty_level - 1)
                    state_attempt.save()

            elif state_attempt.state == 'O':
             
                recent_attempts = QuestionAttempt.objects.filter(
                    state_attempt=state_attempt
                ).order_by('-timestamp')[:5]
                
                if len(recent_attempts) == 5:
                    correct_count = sum(1 for attempt in recent_attempts if attempt.is_correct)
                    if correct_count >= 3:
                        state_attempt.difficulty_level += 1
                    elif correct_count <= 2:
                        state_attempt.difficulty_level = max(1, state_attempt.difficulty_level - 1)
                    state_attempt.save()

     
            next_question, _ = self.generate_arithmetic_question(
                state_attempt.difficulty_level, 
                state_attempt.state
            )

          
            state_templates = {
                'B': 'bored_state.html',
                'F': 'flow_state.html',
                'O': 'overload_state.html',
                'R': 'resting_state.html'
            }
            
            template_name = f'test_app/{state_templates.get(state_attempt.state, "bored_state.html")}'
            
            return render(request, template_name, {
                'session_id': session_id,
                'state_attempt_id': state_attempt_id,
                'question': next_question,
                'state': state_attempt.state,
                'sequence': session.current_sequence,
                'remaining_time': remaining_time  # Pass the remaining time to the template
            })

    def timer_state(self, request, session_id):
        """
        Handle 25-second timer between states
        """
        session = TestSession.objects.get(id=session_id)
        
        # Determine next state in the sequence
        current_sequence = self.SEQUENCES[session.current_sequence - 1]
        current_index = current_sequence.index(session.current_state)
        
        # Move to next state
        next_index = (current_index + 1) % len(current_sequence)
        next_state = current_sequence[next_index]
        
        # Update session
        session.current_state = next_state
        session.save()

        context = {
            'session_id': session_id,
            'next_state': next_state
        }
        return render(request, 'test_app/timer_state.html', context)