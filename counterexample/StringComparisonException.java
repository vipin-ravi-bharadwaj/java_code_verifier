public class StringComparisonException {
    public static void main(String[] args) {
        try {
            String str1 = null;
            String str2 = "Hello";

            // Attempting to compare strings
            if (str1.equals(str2)) {
                System.out.println("Strings are equal.");
            } else {
                System.out.println("Strings are not equal.");
            }
        } catch (NullPointerException e) {
            // Catching the NullPointerException
            System.out.println("StringComparisonException caught: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
