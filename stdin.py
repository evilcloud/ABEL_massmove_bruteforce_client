from logic import run_logic

def get_user_input():
    single_amount_default = 1000
    batch_size_default = 3

    single_amount = int(
        input(f"Enter single amount (default: {single_amount_default}): ") or single_amount_default
    )
    batch_size = int(
        input(f"Enter batch size (default: {batch_size_default}): ") or batch_size_default
    )

    return single_amount, batch_size


if __name__ == "__main__":
    # Get user input
    single_amount, batch_size = get_user_input()

    # Run the logic
    run_logic(single_amount, batch_size)
