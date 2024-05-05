public class ClassCastExceptionExample {
    public static void main(String[] args) {
        try {
            // Creating an Integer object
            Object obj = new Integer(100);

            // Attempting to cast it to String
            String str = (String) obj;

            // This line will not be reached if the cast fails
            System.out.println("Casting successful: " + str);
        } catch (ClassCastException e) {
            // Catching the ClassCastException
            System.out.println("ClassCastException caught: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
